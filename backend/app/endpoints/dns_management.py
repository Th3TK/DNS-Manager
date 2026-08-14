

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dns.management import create_zone, get_zone, get_zones
from app.dns.models.dns_record import CreateDNSRecordForm, DNSRecord
from app.dns.models.dns_zone import CreateDNSZoneArgs, CreateDNSZoneForm, DNSZone
from app.users.authentication import get_authenticated_user
from app.users.models.user import User

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='',
    tags=['DNS Management'],
)

@router.get("/zones", response_model=list[DNSZone])
def __get_all_zones__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)], 
):
    return get_zones(db)

@router.get("/zone", response_model=DNSZone)
def __get_singular_zone__(
    user: Annotated[User, Depends(get_authenticated_user)], 
    db: Annotated[Session, Depends(get_db)], 
    zone_id: str
):
    return get_zone(db, zone_id)


@router.post("/zone", response_model=DNSZone)
def __create_zone__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)], 
    form: CreateDNSZoneForm
):
    logger.debug("Authenticated as:", user.username)

    return create_zone(db, CreateDNSZoneArgs(
        **form.model_dump(),
        author=user.username,
    ))


@router.get("/records", response_model=list[DNSRecord])
def __get_all_zone_records__(zone_id: str):
    pass

@router.get("/record", response_model=DNSRecord)
def __get_singular_record__(zone_id: str, record_name: str, type: str, content: str):
    pass


@router.post("/record", response_model=DNSRecord)
def __create_record__(form: CreateDNSRecordForm):
    pass