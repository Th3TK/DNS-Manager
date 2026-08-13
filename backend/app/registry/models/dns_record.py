from typing import Annotated, Literal

from pydantic import BaseModel, Field

# DNS record types that are supported during record creation via the DNSManager interface
type SupportedDNSRecordTypes = Literal["A", "AAAA", "CNAME", "TXT", "MX", "SRV"]


class DNSRecord(BaseModel):
    """
    Represents a DNS record return model for GET endpoints and websockets.
    For records with `origin="external"` (created independently c the application), some metadata may be unavailable.
    """
    
    zone: str
    name: str
    type: str 
    content: str
    ttl: Annotated[int, Field(gt=0, le=2_147_483_647)]
    
    """
    Metadata
    """
    
    origin: Literal["manual", "automatic => traefik", "external"]
    author: str | None = None # username / "watcher:<WATCHER_NAME>"
    comment: str | None = None
    checks_enabled: bool

    
class CreateDNSRecordForm(BaseModel):
    """
    Represents a DNS record body model for CREATE endpoints.
    """
    name: str
    type: SupportedDNSRecordTypes
    content: str
    ttl: Annotated[int, Field(gt=0, le=2_147_483_647)]
    comment: str | None = None
    checks_enabled: bool = True