import logging
from typing import Literal

import requests
from app.config import ENV_CONFIG
from app.dns.models.record import CreateDNSRecordArgs, DNSRecordIdentifier, DNSRecordProperties, ModifyDNSRecordArgs
from app.dns.models.zone import CreateDNSZoneArgs, DNSZoneProperties
from app.dns.providers.base import DNSProvider
from app.dns.providers.powerdns.models import PowerDNSZone
from app.utils.paths import join_url
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class PowerDNSAdapter(DNSProvider):
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
                    "Connection to the PowerDNS REST API timed out. Try again later"
                    "or check whether your PowerDNS connection settings"
                    "in the environment variables are correctly configured."
                ),
            )
        except requests.exceptions.ConnectionError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Could not connect to the PowerDNS REST API. Ensure that PowerDNS"
                    "service is running and that the PowerDNS connection settings"
                    "in the environment variables are correctly configured."
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
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=(
                        "Authentication with the PowerDNS REST API failed.Verify that POWERDNS_API_KEY contains a valid API key."
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
        return DNSZoneProperties(id=zone.id, name=zone.name)

    def _get_record_properties_from_powerdns_zone(
        self, zone: PowerDNSZone, record_id: DNSRecordIdentifier
    ) -> DNSRecordProperties | None:
        if zone.rrsets is None:
            return None

        for rrset in zone.rrsets:
            if rrset.name != record_id.name or rrset.type != record_id.type or not rrset.records:
                continue

            contents = [record.content for record in rrset.records]
            content = contents[0] if len(contents) == 1 else contents

            return DNSRecordProperties(**record_id.model_dump(), content=content, ttl=rrset.ttl)

        return None

    # ZONES

    def create_zone(self, creation_args: CreateDNSZoneArgs) -> DNSZoneProperties:
        body = {"id": creation_args.name, "name": creation_args.name, "kind": "Native"}
        response = self._send_request("POST", "zones", json=body)
        zone = PowerDNSZone.model_validate(response.json())

        return self._get_zone_properties_from_powerdns_zone(zone)

    def delete_zone(self, zone_id: str) -> None:
        self._send_request("DELETE", f"zones/{zone_id}")

    def get_zones(self) -> list[DNSZoneProperties]:
        response = self._send_request("GET", "zones")
        zones = [PowerDNSZone.model_validate(zone) for zone in response.json()]

        return [self._get_zone_properties_from_powerdns_zone(zone) for zone in zones]

    def get_zone(self, zone_id: str) -> DNSZoneProperties | None:
        response = self._send_request("GET", f"zones/{zone_id}")
        zone = PowerDNSZone.model_validate(response.json())

        return self._get_zone_properties_from_powerdns_zone(zone)

    # RECORDS

    def get_record(self, record_id: DNSRecordIdentifier) -> DNSRecordProperties | None:
        response = self._send_request("GET", f"zones/{record_id.zone_id}?rrsets=true")
        zone = PowerDNSZone.model_validate(response.json())

        return self._get_record_properties_from_powerdns_zone(zone, record_id)

    def get_records(self, zone_id: str) -> list[DNSRecordProperties]:
        response = self._send_request("GET", f"zones/{zone_id}?rrsets=true")
        zone = PowerDNSZone.model_validate(response.json())

        if zone.rrsets is None:
            return []

        records: list[DNSRecordProperties] = []

        for rrset in zone.rrsets:
            contents = [record.content for record in rrset.records]
            content = contents[0] if len(contents) == 1 else contents

            records.append(
                DNSRecordProperties(
                    zone_id=zone_id,
                    name=rrset.name,
                    type=rrset.type,
                    content=content,
                    ttl=rrset.ttl,
                )
            )

        return records

    def create_record(self, creation_args: CreateDNSRecordArgs) -> DNSRecordProperties:
        body = {
            "rrsets": [
                {
                    "name": creation_args.name,
                    "type": creation_args.type,
                    "ttl": creation_args.ttl,
                    "changetype": "REPLACE",
                    "records": [{"content": creation_args.content, "disabled": False}],
                }
            ]
        }

        self._send_request("PATCH", f"zones/{creation_args.zone_id}", json=body)  # returns 204 no content

        record_id = DNSRecordIdentifier.model_validate(creation_args.model_dump())
        record = self.get_record(record_id)

        if record is None:
            logging.error("PowerDNS PATCH succeeded, but the created record could not be retrieved.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the DNS record.",
            )

        return record

    def modify_record(self, modification_args: ModifyDNSRecordArgs) -> DNSRecordProperties:
        body = {
            "rrsets": [
                {
                    "name": modification_args.name,
                    "type": modification_args.type,
                    "ttl": modification_args.ttl,
                    "changetype": "REPLACE",
                    "records": [{"content": modification_args.content, "disabled": False}],
                },
            ]
        }

        self._send_request("PATCH", f"zones/{modification_args.zone_id}", json=body)  # returns 204 no content

        record_id = DNSRecordIdentifier.model_validate(modification_args.model_dump())
        record = self.get_record(record_id)

        if record is None:
            logging.error("PowerDNS PATCH succeeded, but the modified record could not be retrieved.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while modifying the DNS record.",
            )

        return record

    def delete_record(self, record_id: DNSRecordIdentifier) -> None: ...
