import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

import requests
from app.config import ENV_CONFIG
from app.models.record import DNSRecordProperties
from app.models.zone import DNSZoneProperties
from app.providers.base import DNSProvider
from app.providers.powerdns.models import PowerDNSZone
from app.utils.paths import join_url
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class PowerDNSAdapter(DNSProvider):
    """
    Adapter for PowerDNS version 4.9.17
    """

    session: requests.Session
    api_url: str

    def __init__(self):
        self.session = requests.Session()
        self.api_url = join_url(ENV_CONFIG.POWERDNS_API_URL, "servers", ENV_CONFIG.POWERDNS_SERVER_ID)

    def _send_request(self, method: Literal["GET", "DELETE", "POST", "PUT", "PATCH"], path: str, **kwargs) -> requests.Response:
        try:
            response = self.session.request(
                method=method,
                url=join_url(self.api_url, path),
                timeout=10,
                **kwargs,
                headers={
                    "X-API-KEY": ENV_CONFIG.POWERDNS_API_KEY,
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    **kwargs.get("headers", {}),
                },
            )
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Connection to the PowerDNS REST API timed out. Try again later "
                    "or check whether your PowerDNS connection settings "
                    "in the environment variables are correctly configured. "
                ),
            )
        except requests.exceptions.ConnectionError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Could not connect to the PowerDNS REST API. Ensure that PowerDNS "
                    "service is running and that the PowerDNS connection settings "
                    "in the environment variables are correctly configured. "
                ),
            )
        except requests.exceptions.HTTPError as exc:
            if exc.response is None:
                logger.error("The PowerDNS REST API returned an invalid HTTP response.", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="The PowerDNS REST API returned an invalid HTTP response.",
                )

            if exc.response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=(
                        "Authentication with the PowerDNS REST API failed. Verify that POWERDNS_API_KEY contains a valid API key."
                    ),
                )

            try:
                body = exc.response.json()
            except requests.exceptions.JSONDecodeError:
                body = None

            powerdns_error = body.get("error") if isinstance(body, dict) else None

            raise HTTPException(status_code=exc.response.status_code, detail=powerdns_error)

        except requests.exceptions.RequestException as exc:
            logger.error("Unhandled error occured while trying to communicate with the PowerDNS REST API.", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to communicate with the PowerDNS REST API.",
            )

    def _get_zone_properties_from_powerdns_zone(self, zone: PowerDNSZone) -> DNSZoneProperties:
        return DNSZoneProperties(name=zone.name, record_count=sum(len(rrset.records) for rrset in zone.rrsets or []))

    def _get_record_properties_from_powerdns_zone(
        self,
        zone: PowerDNSZone,
        name: str,
        type_: str,
    ) -> DNSRecordProperties | None:
        if zone.rrsets is None:
            return None

        for rrset in zone.rrsets:
            if rrset.name != name or rrset.type != type_ or not rrset.records:
                continue

            contents = [record.content for record in rrset.records]
            content = contents[0] if len(contents) == 1 else contents

            return DNSRecordProperties(
                zone_name=zone.name,
                name=name,
                type=type_,
                content=content,
                ttl=rrset.ttl,
            )

        return None

    # MISC

    def health_check(self) -> None:
        try:
            self._send_request("GET", "")
        except HTTPException as exc:
            match exc.status_code:
                case status.HTTP_404_NOT_FOUND:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=(
                            "Could not retrieve data from the PowerDNS server due to an invalid path. "
                            "Ensure the POWERDNS_SERVER_ID environment variable is set correctly."
                        ),
                    )
                case status.HTTP_502_BAD_GATEWAY:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=exc.detail,
                    )
                case status.HTTP_503_SERVICE_UNAVAILABLE:
                    raise exc
                case _:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=(
                            "Error occured while trying to connect to PowerDNS REST API. Ensure that PowerDNS "
                            "service is running and that the PowerDNS connection settings "
                            "in the environment variables are correctly configured."
                        ),
                    )

    # ZONES

    def create_zone(self, zone_name: str) -> DNSZoneProperties:
        body = {"name": zone_name, "kind": "Native"}
        response = self._send_request("POST", "zones", json=body)
        zone = PowerDNSZone.model_validate(response.json())

        return self._get_zone_properties_from_powerdns_zone(zone)

    def delete_zone(self, zone_name: str) -> None:
        self._send_request("DELETE", f"zones/{zone_name}")

    def get_zones(self) -> list[DNSZoneProperties]:
        response = self._send_request("GET", "zones?dnssec=false")
        zone_names = [PowerDNSZone.model_validate(zone).name for zone in response.json()]

        # retrieving data such as record_count
        with ThreadPoolExecutor() as executor:
            zones = executor.map(self.get_zone, zone_names)

        return [zone for zone in zones if zone is not None]

    def get_zone(
        self,
        zone_name: str,
    ) -> DNSZoneProperties | None:
        try:
            response = self._send_request("GET", f"zones/{zone_name}")
        except HTTPException as exc:
            if exc.status_code == status.HTTP_404_NOT_FOUND:
                return
            raise exc
        zone = PowerDNSZone.model_validate(response.json())

        return self._get_zone_properties_from_powerdns_zone(zone)

    # RECORDS

    def get_record(
        self,
        zone_name: str,
        name: str,
        type_: str,
    ) -> DNSRecordProperties | None:
        try:
            response = self._send_request("GET", f"zones/{zone_name}?rrsets=true")
        except HTTPException as exc:
            if exc.status_code == status.HTTP_404_NOT_FOUND:
                return None
            raise exc

        zone = PowerDNSZone.model_validate(response.json())

        return self._get_record_properties_from_powerdns_zone(zone, name, type_)

    def get_records(self, zone_name: str) -> list[DNSRecordProperties] | None:
        try:
            response = self._send_request("GET", f"zones/{zone_name}?rrsets=true")
        except HTTPException as exc:
            if exc.status_code == status.HTTP_404_NOT_FOUND:
                return None
            raise exc

        zone = PowerDNSZone.model_validate(response.json())

        if zone.rrsets is None:
            return []

        records: list[DNSRecordProperties] = []

        for rrset in zone.rrsets:
            contents = [record.content for record in rrset.records]
            content = contents[0] if len(contents) == 1 else contents

            records.append(
                DNSRecordProperties(
                    zone_name=zone_name,
                    name=rrset.name,
                    type=rrset.type,
                    content=content,
                    ttl=rrset.ttl,
                )
            )

        return records

    def create_record(self, zone_name: str, name: str, type_: str, content: str, ttl: int) -> DNSRecordProperties:
        # modify_record accomplishes the same thing
        return self.modify_record(zone_name, name, type_, content, ttl)

    def modify_record(self, zone_name: str, name: str, type_: str, content: str, ttl: int) -> DNSRecordProperties:
        body = {
            "rrsets": [
                {
                    "name": name,
                    "type": type_,
                    "ttl": ttl,
                    "changetype": "REPLACE",
                    "records": [{"content": content, "disabled": False}],
                },
            ]
        }

        self._send_request("PATCH", f"zones/{zone_name}", json=body)  # returns 204 no content

        record = self.get_record(zone_name, name, type_)

        if record is None:
            logging.error("PowerDNS PATCH succeeded, but the modified record could not be retrieved.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while modifying the DNS record.",
            )

        return record

    def delete_record(self, zone_name: str, name: str, type_: str) -> None:
        body = {"rrsets": [{"name": name, "type": type_, "changetype": "DELETE"}]}

        self._send_request("PATCH", f"zones/{zone_name}", json=body)  # returns 204 no content
