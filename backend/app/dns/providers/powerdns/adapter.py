import logging
from typing import Literal

import requests
from app.config import ENV_CONFIG
from app.dns.models.record import CreateDNSRecordArgs, DNSRecord, DNSRecordIdentifier, DNSRecordProperties
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

    def _send_request(self, method: Literal["GET", "DELETE", "POST", "PUT"], path: str, **kwargs) -> requests.Response:
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

    def create_zone(self, creation_args: CreateDNSZoneArgs) -> DNSZoneProperties:
        body = {"id": creation_args.name, "name": creation_args.name, "kind": "Native"}
        response = self._send_request("POST", "zones", json=body)
        zone = PowerDNSZone.model_validate(response.json())

        return DNSZoneProperties(id=zone.id, name=zone.name)

    def delete_zone(self, zone_id: str) -> None:
        self._send_request("DELETE", f"zones/{zone_id}")

    def get_zones(self) -> list[DNSZoneProperties]:
        response = self._send_request("GET", "zones")
        zones = [PowerDNSZone.model_validate(zone) for zone in response.json()]

        return [DNSZoneProperties(id=zone.id, name=zone.name) for zone in zones]

    def get_zone(self, zone_id: str) -> DNSZoneProperties | None:
        response = self._send_request("GET", f"zones/{zone_id}")
        zone = PowerDNSZone.model_validate(response.json())

        return DNSZoneProperties(id=zone.id, name=zone.name)

    def create_record(self, creation_args: CreateDNSRecordArgs) -> DNSRecord: ...

    def modify_record(
        self, record_id: DNSRecordIdentifier, modification_args: CreateDNSRecordArgs
    ) -> DNSRecordProperties | None: ...

    def delete_record(self, record_id: DNSRecordIdentifier) -> None: ...

    def get_records(self, zone_id: str) -> list[DNSRecordProperties]: ...

    def get_record(self, record_id: DNSRecordIdentifier) -> DNSRecordProperties | None: ...
