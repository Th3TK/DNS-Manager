from typing import Annotated, Literal

from app.database.models.dns_zone_metadata import DNSZoneMetadataInDB
from pydantic import BaseModel, Field, field_validator

type DNSZoneOrigin = Literal["manual", "external"]


class DNSZoneProperties(BaseModel):
    """
    Properties of a DNS zone managed by the DNS provider.
    """

    id: str
    name: str


class DNSZoneMetadata(BaseModel):
    """
    Additional DNS zone metadata stored in the application's database.
    """

    origin: DNSZoneOrigin
    comment: str | None = None
    author: str | None = None  # username

    @classmethod
    def from_db(cls, metadata_db: DNSZoneMetadataInDB | None) -> "DNSZoneMetadata":
        if metadata_db is None:
            return cls(origin="external")

        return cls(
            origin="manual",
            author=metadata_db.author,
            comment=metadata_db.comment,
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
    comment: Annotated[str | None, Field(max_length=1000, default=None)]

    @field_validator("name", mode="after")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return f"{value.rstrip('.')}."


class CreateDNSZoneArgs(CreateDNSZoneForm):
    """
    Arguments for creating a DNS zone.
    Extends the API request data with properties determined by the backend, rather than supplied by the client.
    """

    origin: DNSZoneOrigin
    author: str  # username
