

from fastapi import APIRouter

from app.registry.models.dns_record import CreateDNSRecordForm, DNSRecord
from app.registry.models.dns_zone import CreateDNSZoneForm, DNSZone

router = APIRouter(
    prefix='',
    tags=['DNS Management'],
)

@router.get("/zones", response_model=list[DNSZone])
def get_all_zones():
    pass

@router.get("/zone", response_model=DNSZone)
def get_singular_zone(zone_name: str):
    pass

@router.get("/records", response_model=list[DNSRecord])
def get_all_zone_records(zone_name: str):
    pass

@router.get("/record", response_model=DNSRecord)
def get_singular_record(zone_name: str, record_name: str, type: str, content: str):
    pass

@router.post("/zone", response_model=DNSZone)
def create_zone(form: CreateDNSZoneForm):
    pass

@router.post("/record", response_model=DNSRecord)
def create_record(form: CreateDNSRecordForm):
    pass