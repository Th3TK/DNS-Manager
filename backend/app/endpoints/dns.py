import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.management.dns.record import create_record, delete_record, get_all_records, get_record, get_records, modify_record
from app.management.dns.zone import create_zone, delete_zone, get_zone, get_zones
from app.management.users.authentication import get_authenticated_administrator, get_authenticated_user
from app.models.record import (
    CreateDNSRecordArgs,
    CreateDNSRecordForm,
    DNSRecord,
    DNSRecordRemovalResult,
    ModifyDNSRecordArgs,
    ModifyDNSRecordForm,
    SupportedDNSRecordTypes,
)
from app.models.user import User
from app.models.zone import CreateDNSZoneArgs, CreateDNSZoneForm, DNSZone, DNSZoneRemovalResult

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="",
    tags=["DNS Management"],
)


@router.get("/zones", response_model=list[DNSZone])
def __get_all_zones__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[DNSZone]:
    return get_zones(db)


@router.get("/zones/{zone_name}", response_model=DNSZone)
def __get_singular_zone__(
    user: Annotated[User, Depends(get_authenticated_user)], db: Annotated[Session, Depends(get_db)], zone_name: str
) -> DNSZone:
    return get_zone(db, zone_name)


@router.post("/zones", response_model=DNSZone, status_code=201)
def __create_zone__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    form: CreateDNSZoneForm,
):
    return create_zone(db, CreateDNSZoneArgs(**form.model_dump(), author=user.username))


@router.delete("/zones/{zone_name}", response_model=DNSZoneRemovalResult, status_code=200)
def __delete_zone__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    zone_name: str,
) -> DNSZoneRemovalResult:
    return delete_zone(db, zone_name, user)


@router.get("/all-records", response_model=list[DNSRecord])
def __get_all_records__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[DNSRecord]:
    return get_all_records(db)


@router.get("/zones/{zone_name}/records", response_model=list[DNSRecord])
def __get_all_zone_records__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    zone_name: str,
) -> list[DNSRecord]:
    return get_records(db, zone_name)


@router.get("/zones/{zone_name}/record", response_model=DNSRecord)
def __get_singular_record_details__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    zone_name: str,
    record_name: str,
    record_type: str,
) -> DNSRecord:
    return get_record(db, zone_name=zone_name, name=record_name, type_=record_type)


@router.post("/zones/{zone_name}/record", response_model=DNSRecord, status_code=201)
def __create_record__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    zone_name: str,
    form: CreateDNSRecordForm,
) -> DNSRecord:
    return create_record(
        db,
        CreateDNSRecordArgs(
            **form.model_dump(),
            author=user.username,
            zone_name=zone_name,
            origin="manual",
        ),
    )


@router.patch("/zones/{zone_name}/record", response_model=DNSRecord)
def __modify_record__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    zone_name: str,
    record_name: str,
    record_type: SupportedDNSRecordTypes,
    form: ModifyDNSRecordForm,
) -> DNSRecord:
    return modify_record(
        db=db,
        zone_name=zone_name,
        name=record_name,
        type_=record_type,
        modification_args=ModifyDNSRecordArgs(**form.model_dump(), author=user.username),
    )


@router.delete("/zones/{zone_name}/record", response_model=DNSRecordRemovalResult, status_code=200)
def __delete_record__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    zone_name: str,
    record_name: str,
    record_type: str,
) -> DNSRecordRemovalResult:
    return delete_record(
        db=db,
        zone_name=zone_name,
        name=record_name,
        type_=record_type,
        logged_in_user=user,
    )
