from typing import Protocol

from app.models.record import DNSRecordProperties
from app.models.zone import DNSZoneProperties


class DNSProvider(Protocol):
    def health_check(self) -> None:
        """
        Checks whether the provider is reachable. Must raise `HTTP 503` if any error occurs; no other status codes are permitted.
        Returns `None` on success.
        """
        ...

    def get_zone(self, zone_name: str) -> DNSZoneProperties | None:
        """
        Retrieves the zone properties and returns them.
        If the zone does not exist in the provider returns `None`.
        """
        ...

    def get_zones(self) -> list[DNSZoneProperties]:
        """
        Retrieves all zones and returns their properties in a list.
        """
        ...

    def create_zone(self, zone_name: str) -> DNSZoneProperties:
        """
        Creates a zone of type/kind Native with a provided zone_name.
        Returns properties of the created zone.
        """
        ...

    def delete_zone(self, zone_name: str) -> None:
        """
        Deletes the zone from the provider and all its records.
        """
        ...

    def get_record(self, zone_name: str, name: str, type_: str) -> DNSRecordProperties | None:
        """
        Retrieves record properties and returns them.
        If the zone or the record does not exist in the provider returns `None`.
        """
        ...

    def get_records(self, zone_name: str) -> list[DNSRecordProperties] | None:
        """
        Retrieves all records in a zone and returns their properties in a list.
        Returns an empty list if the zone has no records.
        Returns `None` if the zone does not exist.
        """
        ...

    def create_record(self, zone_name: str, name: str, type_: str, content: str, ttl: int) -> DNSRecordProperties:
        """
        Creates a new record in the provided zone.
        It is guaranteed that no other record with the same (zone_name, name, type_) already exists.
        Returns the created record properties.
        """
        ...

    def modify_record(self, zone_name: str, name: str, type_: str, content: str, ttl: int) -> DNSRecordProperties:
        """
        Modifies an existing record's content and time-to-live.
        It is guaranteed that the record exists.
        Returns the modified record properties.
        """
        ...

    def delete_record(self, zone_name: str, name: str, type_: str) -> None:
        """
        Deletes a record from the zone.
        """
        ...
