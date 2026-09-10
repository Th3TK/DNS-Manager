import logging
import re
from typing import Literal

import requests
from app.config import ENV_CONFIG
from app.models.exceptions import DNSProviderException
from app.models.record import DNSRecordProperties
from app.models.zone import DNSZoneProperties
from app.providers.base import DNSProvider
from app.providers.powerdns.models import PowerDNSSearchResultRecord, PowerDNSZone
from app.utils.paths import join_url
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class PowerDNSAdapter_4_9_17(DNSProvider):
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
            raise DNSProviderException(
                "Connection to the PowerDNS REST API timed out. Try again later "
                "or check whether your PowerDNS connection settings "
                "in the environment variables are correctly configured. "
            )
        except requests.exceptions.ConnectionError:
            raise DNSProviderException(
                "Could not connect to the PowerDNS REST API. Ensure that PowerDNS "
                "service is running and that the PowerDNS connection settings "
                "in the environment variables are correctly configured. "
            )
        except requests.exceptions.HTTPError as exc:
            if exc.response is None:
                logger.error("The PowerDNS REST API returned an invalid HTTP response.", exc)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="The PowerDNS REST API returned an invalid HTTP response.",
                )

            if exc.response.status_code == 401:
                raise DNSProviderException(
                    "Authentication with the PowerDNS REST API failed. Verify that POWERDNS_API_KEY contains a valid API key."
                )

            try:
                body = exc.response.json()
            except requests.exceptions.JSONDecodeError:
                body = None

            powerdns_error = body.get("error") if isinstance(body, dict) else None

            raise HTTPException(status_code=exc.response.status_code, detail=powerdns_error)

        except requests.exceptions.RequestException as exc:
            logger.error("Unhandled error occured while trying to communicate with the PowerDNS REST API.", exc)
            raise DNSProviderException("Failed to communicate with the PowerDNS REST API.")

    def _get_zone_properties_from_powerdns_zone(self, zone: PowerDNSZone) -> DNSZoneProperties:
        return DNSZoneProperties(
            name=zone.name,
            record_count=sum(len(rrset.records) for rrset in zone.rrsets) if zone.rrsets is not None else None,
        )

    def _get_records_properties_from_powerdns_zone(
        self,
        zone: PowerDNSZone,
        name: str | None = None,
        type_: str | None = None,
    ) -> list[DNSRecordProperties]:

        if zone.rrsets is None:
            return []

        records: list[DNSRecordProperties] = []

        for rrset in zone.rrsets:
            if name is not None and rrset.name != name:
                continue

            if type_ is not None and rrset.type != type_:
                continue

            contents = [record.content for record in rrset.records]
            content = contents[0] if len(contents) == 1 else contents

            records.append(
                DNSRecordProperties(
                    zone_name=zone.name,
                    name=rrset.name,
                    type=rrset.type,
                    content=content,
                    ttl=rrset.ttl,
                )
            )

        return records

    # -------------------------------------------------------------------------
    # MISC
    # -------------------------------------------------------------------------

    def health_check(self) -> None:
        try:
            self._send_request("GET", "")
        except DNSProviderException as exc:
            raise exc
        except HTTPException as exc:
            match exc.status_code:
                case status.HTTP_404_NOT_FOUND:
                    raise DNSProviderException(
                        "Could not retrieve data from the PowerDNS server due to an invalid path. "
                        "Ensure the POWERDNS_SERVER_ID environment variable is set correctly."
                    )
                case status.HTTP_502_BAD_GATEWAY:
                    raise DNSProviderException(exc.detail)
                case _:
                    raise DNSProviderException(
                        "Error occured while trying to connect to PowerDNS REST API. Ensure that PowerDNS "
                        "service is running and that the PowerDNS connection settings "
                        "in the environment variables are correctly configured."
                    )

    # -------------------------------------------------------------------------
    # ZONES
    # -------------------------------------------------------------------------

    def create_zone(self, zone_name: str) -> DNSZoneProperties:
        body = {"name": zone_name, "kind": "Native"}
        response = self._send_request("POST", "zones", json=body)
        zone = PowerDNSZone.model_validate(response.json())

        return self._get_zone_properties_from_powerdns_zone(zone)

    def delete_zone(self, zone_name: str) -> None:
        self._send_request("DELETE", f"zones/{zone_name}")

    def get_zones(self, skip_record_count: bool = False) -> list[DNSZoneProperties]:
        response = self._send_request("GET", "zones?dnssec=false")
        powerdns_zones = [PowerDNSZone.model_validate(zone) for zone in response.json()]

        zones_by_name = {
            powerdns_zone.name: self._get_zone_properties_from_powerdns_zone(powerdns_zone) for powerdns_zone in powerdns_zones
        }

        if skip_record_count:
            return list(zones_by_name.values())

        # counting records

        # names = [powerdns_zone.name for powerdns_zone in powerdns_zones]

        # # count records
        # with ThreadPoolExecutor(max_workers=10) as executor:
        #     zones = executor.map(self.get_zone, names)

        # using query is much faster than sending seperate requests for each zone
        all_records = self.query_records("*")

        if all_records is not None:
            for record in all_records:
                zone = zones_by_name[record.zone_name]

                if zone is not None:
                    zone.record_count = (zone.record_count or 0) + 1

        return list(zones_by_name.values())

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

    # -------------------------------------------------------------------------
    # RECORDS
    # -------------------------------------------------------------------------

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

        matched = self._get_records_properties_from_powerdns_zone(zone, name, type_)
        return matched[0] if matched else None

    def get_records_by_name(self, zone_name: str, name: str) -> list[DNSRecordProperties] | None:
        try:
            response = self._send_request("GET", f"zones/{zone_name}?rrsets=true")
        except HTTPException as exc:
            if exc.status_code == status.HTTP_404_NOT_FOUND:
                return None
            raise exc

        zone = PowerDNSZone.model_validate(response.json())

        return self._get_records_properties_from_powerdns_zone(zone, name)

    def get_records(self, zone_name: str) -> list[DNSRecordProperties] | None:
        try:
            response = self._send_request("GET", f"zones/{zone_name}?rrsets=true")
        except HTTPException as exc:
            if exc.status_code == status.HTTP_404_NOT_FOUND:
                return None
            raise exc
        zone = PowerDNSZone.model_validate(response.json())

        return self._get_records_properties_from_powerdns_zone(zone)

    def query_records(self, name_query: str) -> list[DNSRecordProperties] | None:
        # search-data matches both record names and content
        # we'll have to filter out content matches but it's still faster than fetching all records
        response = self._send_request("GET", f"search-data?q={name_query.rstrip('.')}&object_type=record&max=100000")

        pattern = re.escape(name_query.rstrip("."))
        pattern = pattern.replace(r"\*", ".*").replace(r"\?", ".")
        pattern = f"^{pattern}{re.escape('.')}$"

        # DNSRecordProperties has to represent an RRset for consistency with the rest of the application
        # we're grouping contents from records with equal keys (zone_name, name, type)
        record_contents: dict[tuple[str, str, str], list[str]] = {}
        record_properties: dict[tuple[str, str, str], PowerDNSSearchResultRecord] = {}

        for entry in response.json():
            record = PowerDNSSearchResultRecord.model_validate(entry)

            # filter out the content matches
            if not re.fullmatch(pattern, record.name):
                continue

            key = (record.zone, record.name, record.type)

            if key not in record_contents:
                record_contents[key] = []
                record_properties[key] = record

            record_contents[key].append(record.content)

        records = []

        for key, contents in record_contents.items():
            record = record_properties[key]

            records.append(
                DNSRecordProperties(
                    zone_name=record.zone,
                    name=record.name,
                    content=contents if len(contents) > 1 else contents[0],
                    type=record.type,
                    ttl=record.ttl,
                )
            )

        return records

    def create_record(self, zone_name: str, name: str, type_: str, content: str, ttl: int) -> DNSRecordProperties:
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

    def modify_record(
        self, zone_name: str, name: str, type_: str, new_name: str, new_type: str, new_content: str, new_ttl: int
    ) -> DNSRecordProperties:
        body = {
            "rrsets": [
                {"name": name, "type": type_, "changetype": "DELETE"},
                {
                    "name": new_name,
                    "type": new_type,
                    "ttl": new_ttl,
                    "changetype": "REPLACE",
                    "records": [{"content": new_content, "disabled": False}],
                },
            ]
        }

        self._send_request("PATCH", f"zones/{zone_name}", json=body)  # returns 204 no content

        record = self.get_record(zone_name, new_name, new_type)

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
