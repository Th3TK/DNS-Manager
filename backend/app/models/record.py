import datetime
from typing import Annotated, Literal, cast
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.database.models.dns_record_metadata import DNSRecordMetadataInDB
from app.database.models.enums import ChangeAction

# DNS record types that are supported during record creation via the DNSManager interface
type SupportedDNSRecordTypes = Literal["A", "AAAA", "CNAME", "TXT", "MX", "SRV"]

type DNSRecordOrigin = Literal["manual", "automatic => traefik", "external"]

type DNSRecordOriginInternal = Literal["manual", "automatic => traefik"]


class DNSRecordIdentifier(BaseModel):
    """
    Contains the fields required to uniquely identify a DNS record.
    """

    zone_name: str
    name: str
    type: str


class DNSRecordProperties(BaseModel):
    """
    Properties of a DNS record managed by the DNS provider.
    """

    zone_name: str
    name: str
    type: str
    content: str | list[str]
    ttl: Annotated[int, Field(gt=0, le=2_147_483_647)]


class DNSRecordMetadata(BaseModel):
    """
    Additional DNS record metadata stored in the application's database.
    """

    origin: DNSRecordOrigin
    author: str | None = None  # username / "watcher:<WATCHER_NAME>"
    comment: str | None = None
    checks_enabled: bool

    @classmethod
    def from_db(cls, metadata_db: DNSRecordMetadataInDB | None) -> "DNSRecordMetadata":
        if metadata_db is None:
            return cls(origin="external", checks_enabled=False)

        return cls(
            origin=cast(DNSRecordOrigin, metadata_db.origin),
            author=metadata_db.author,
            comment=metadata_db.comment,
            checks_enabled=metadata_db.checks_enabled,
        )


class DNSRecord(DNSRecordProperties, DNSRecordMetadata):
    """
    Represents a DNS record response model for GET endpoints and websockets.
    For records with `origin="external"` (created independently of the application), some metadata may be unavailable.
    """

    pass


class CreateDNSRecordForm(BaseModel):
    """
    Request body for creating a DNS record.
    Contains the DNS record properties supplied by the client.
    """

    name: Annotated[str, Field(max_length=255)]
    type: SupportedDNSRecordTypes
    content: Annotated[str, Field(max_length=255)]
    ttl: Annotated[int, Field(gt=0, le=2_147_483_647)] = 60
    comment: Annotated[str, Field(max_length=1000)] | None = None
    checks_enabled: bool = True

    @field_validator("name", mode="after")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return f"{value.rstrip('.').lower()}."


class CreateDNSRecordArgs(CreateDNSRecordForm):
    """
    Arguments for creating a DNS record.
    Extends the API request data with properties determined by the backend, rather than supplied by the client.
    """

    zone_name: Annotated[str, Field(max_length=255)]
    author: str
    origin: DNSRecordOriginInternal

    @field_validator("zone_name", mode="after")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return f"{value.rstrip('.').lower()}."


class ModifyDNSRecordForm(BaseModel):
    """
    Request body for modifying a DNS record.
    Contains the DNS record properties supplied by the client.
    """

    name: Annotated[str, Field(max_length=255)] | None = None
    type: SupportedDNSRecordTypes | None = None
    content: Annotated[str, Field(max_length=255)] | None = None
    ttl: Annotated[int, Field(gt=0, le=2_147_483_647)] | None = None
    comment: Annotated[str, Field(max_length=1000)] | None = None
    checks_enabled: bool | None = None

    @field_validator("name", mode="after")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return f"{value.rstrip('.').lower()}."


class ModifyDNSRecordArgs(ModifyDNSRecordForm):
    """
    Arguments for modifying a DNS record.
    Extends the API request data with properties determined by the backend, rather than supplied by the client.
    """

    author: str


class DNSRecordRemovalResult(BaseModel):
    record_status: Literal[ChangeAction.PERMANENTLY_DELETED, ChangeAction.DELETED]


class DNSRecordSearchResult(BaseModel):
    zone_name: str
    name: str
    type: str
    content: str | list[str]
    origin: DNSRecordOrigin
    location: Literal["active", "trash"]
    trash_entry_uuid: UUID | None = None  # if applicable - uuid of the trash entry


type ResolutionStatus = Literal["OK", "MISMATCH", "NO_RESOLUTION"]

type ReachabilityStatus = Literal["REACHABLE", "UNREACHABLE", "NOT_CHECKED"]


class RecordStatus(BaseModel):
    resolution: ResolutionStatus
    reachability: ReachabilityStatus | None


type RecordStatuses = dict[str, dict[str, dict[str, RecordStatus | None]]]


class RecordStatusCheckData(BaseModel):
    # [zone_name, [name, [type, RESULT | None]]]
    statuses: RecordStatuses | None
    timestamp: datetime.datetime
    next_check: datetime.datetime
