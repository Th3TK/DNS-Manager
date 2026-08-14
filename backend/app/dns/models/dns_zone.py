from typing import Literal

from pydantic import BaseModel

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
    author: str | None = None # username
    

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
    name: str
    comment: str
    

class CreateDNSZoneArgs(CreateDNSZoneForm):
    """
    Arguments for creating a DNS zone.
    Extends the API request data with properties determined by the backend, rather than supplied by the client.
    """
    origin: Literal["manual"] = "manual"
    author: str # username