from typing import Annotated, Literal

from app.database.models.dns_zone_metadata import DNSZoneMetadataInDB
from app.database.models.enums import ChangeAction
from pydantic import BaseModel, Field, field_validator


class DNSZoneProperties(BaseModel):
    """
    Properties of a DNS zone managed by the DNS provider.
    """

    name: str
    record_count: int | None


class DNSZoneMetadata(BaseModel):
    """
    Additional DNS zone metadata stored in the application's database.
    """

    comment: str = ""
    author: str | None = None  # username

    @classmethod
    def from_db(cls, metadata_db: DNSZoneMetadataInDB | None) -> "DNSZoneMetadata":
        if metadata_db is None:
            return cls()

        return cls(
            author=metadata_db.author,
            comment=metadata_db.comment or "",
        )


class DNSZone(DNSZoneProperties, DNSZoneMetadata):
    """
    Represents a DNS zone response model for GET endpoints and websockets.
    For zones with `origin="external"` (created independently of the application), some metadata may be unavailable.
    """

    pass


class CreateDNSZoneForm(BaseModel):
    """
    Request body for creating a DNS zone.
    Contains the DNS zone properties supplied by the client.
    """

    name: Annotated[str, Field(max_length=255)]
    comment: Annotated[str, Field(max_length=1000)] = ""

    @field_validator("name", mode="after")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return f"{value.rstrip('.').lower()}."


class CreateDNSZoneArgs(CreateDNSZoneForm):
    """
    Arguments for creating a DNS zone.
    Extends the API request data with properties determined by the backend, rather than supplied by the client.
    """

    author: str  # username


class DNSZoneRemovalResult(BaseModel):
    zone_status: Literal[ChangeAction.PERMANENTLY_DELETED, ChangeAction.DELETED]
    internal_records_status: Literal[ChangeAction.PERMANENTLY_DELETED, ChangeAction.DELETED]


DNSZoneSortField = Literal[
    "name",
    "author",
    "comment",
]
