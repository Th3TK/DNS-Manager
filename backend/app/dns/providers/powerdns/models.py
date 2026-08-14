
from typing import Literal

from pydantic import BaseModel


class PowerDNSComment(BaseModel):
    account: str
    content: str
    modified_at: int
    
    
class PowerDNSRecordObject(BaseModel):
    content: str
    disabled: bool


class PowerDNSRRset(BaseModel):
    name: str
    records: list[PowerDNSRecordObject]
    ttl: int
    type: str
    changetype: str | None = None
    comments: list[PowerDNSComment] | None = None
    write_unchanged: bool | None = None
    

class PowerDNSZone(BaseModel):
    id: str
    name: str
    type: str | None = None
    url: str | None = None
    kind: str | None = None
    record_count: int | None = None
    rrsets: list[PowerDNSRRset] | None = None
    serial: int | None = None
    notified_serial: int | None = None
    edited_serial: int | None = None
    masters: list[str] | None = None
    dnssec: bool | None = None
    nsec3param: str | None = None
    nsec3narrow: bool | None = None
    presigned: bool | None = None
    soa_edit: str | None = None
    soa_edit_api: str | None = None
    api_rectify: bool | None = None
    zone: str | None = None
    catalog: str | None = None
    account: str | None = None
    nameservers: list[str] | None = None
    master_tsig_key_ids: list[str] | None = None
    slave_tsig_key_ids: list[str] | None = None
    last_check: int | None = None
    
    
class CreatePowerDNSZoneForm(BaseModel):
    name: str
    kind: Literal['Native']