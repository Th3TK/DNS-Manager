from typing import Literal

from pydantic import BaseModel


class DNSZone(BaseModel):
    """
    Represents a DNS zone return model for GET endpoints and websockets.
    For zones with `origin="external"` (created independently of the application), some various metadata may be unavailable.
    """
    
    id: str
    name: str
    type: str
    
    """
    Metadata
    """
        
    origin: Literal["manual", "external"]
    comment: str
    author: str # username
    

class CreateDNSZoneForm(BaseModel):
    """
    Represents a DNS zone body model for CREATE endpoints.
    """
    name: str
    comment: str