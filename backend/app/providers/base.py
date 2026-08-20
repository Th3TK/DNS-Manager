from typing import Protocol

from app.models.record import CreateDNSRecordArgs, DNSRecordIdentifier, DNSRecordProperties, ModifyDNSRecordArgs
from app.models.zone import CreateDNSZoneArgs, DNSZoneProperties


class DNSProvider(Protocol):
    def health_check(self) -> None:
        """
        Raises HTTP 503 if the DNS provider is unavailable.
        """
        ...

    def create_zone(self, creation_args: CreateDNSZoneArgs) -> DNSZoneProperties: ...

    def delete_zone(self, zone_name: str) -> None:
        """
        Deletes the DNS zone and all its records.
        """
        ...

    def get_zones(self) -> list[DNSZoneProperties]: ...

    def get_zone(self, zone_name: str) -> DNSZoneProperties | None: ...

    def create_record(self, creation_args: CreateDNSRecordArgs) -> DNSRecordProperties: ...

    def modify_record(self, modification_args: ModifyDNSRecordArgs) -> DNSRecordProperties: ...

    def delete_record(self, record_id: DNSRecordIdentifier) -> None: ...

    def get_records(self, zone_name: str) -> list[DNSRecordProperties]: ...

    def get_record(self, record_id: DNSRecordIdentifier) -> DNSRecordProperties | None: ...
