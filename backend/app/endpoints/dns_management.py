import logging
from typing import Annotated, Literal

from app.database.database import get_db
from app.database.models.enums import ChangeAction
from app.dns.management.record import create_record, delete_record, get_record, get_records, modify_record
from app.dns.management.zone import create_zone, delete_zone, get_zone, get_zones
from app.dns.models.record import (
    CreateDNSRecordArgs,
    CreateDNSRecordForm,
    DNSRecord,
    DNSRecordIdentifier,
    ModifyDNSRecordArgs,
    ModifyDNSRecordForm,
)
from app.dns.models.zone import CreateDNSZoneArgs, CreateDNSZoneForm, DNSZone
from app.users.authentication import get_authenticated_administrator, get_authenticated_user
from app.users.models.user import User
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/zones",
    tags=["DNS Management"],
)


class RemovalResponse(BaseModel):
    status: Literal[ChangeAction.PERMANENTLY_DELETED, ChangeAction.DELETED]


@router.get("", response_model=list[DNSZone])
def __get_all_zones__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[DNSZone]:
    return get_zones(db)


@router.get("/{zone_id}", response_model=DNSZone)
def __get_singular_zone__(
    user: Annotated[User, Depends(get_authenticated_user)], db: Annotated[Session, Depends(get_db)], zone_id: str
) -> DNSZone:
    return get_zone(db, zone_id)


@router.post("", response_model=DNSZone, status_code=201)
def __create_zone__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    form: CreateDNSZoneForm,
):
    return create_zone(db, CreateDNSZoneArgs(**form.model_dump(), author=user.username))


@router.delete("/{zone_id}", response_model=RemovalResponse, status_code=200)
def __delete_zone__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    zone_id: str,
) -> RemovalResponse:
    return RemovalResponse(status=delete_zone(db, zone_id, user))


@router.get("/{zone_id}/records", response_model=list[DNSRecord])
def __get_all_zone_records__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    zone_id: str,
) -> list[DNSRecord]:
    return get_records(db, zone_id)


@router.get("/{zone_id}/record", response_model=DNSRecord)
def __get_singular_record_details__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    zone_id: str,
    record_name: str,
    record_type: str,
) -> DNSRecord:
    return get_record(db, DNSRecordIdentifier(zone_id=zone_id, name=record_name, type=record_type))


@router.post("/{zone_id}/record", response_model=DNSRecord, status_code=201)
def __create_record__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    zone_id: str,
    form: CreateDNSRecordForm,
) -> DNSRecord:
    return create_record(
        db,
        CreateDNSRecordArgs(
            **form.model_dump(),
            author=user.username,
            zone_id=zone_id,
            origin="manual",
        ),
    )


@router.patch("/{zone_id}/record", response_model=DNSRecord)
def __modify_record__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    zone_id: str,
    form: ModifyDNSRecordForm,
) -> DNSRecord:
    return modify_record(
        db,
        ModifyDNSRecordArgs(
            **form.model_dump(),
            author=user.username,
            zone_id=zone_id,
        ),
    )


@router.delete("/{zone_id}/record", response_model=RemovalResponse, status_code=200)
def __delete_record__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    zone_id: str,
    record_name: str,
    record_type: str,
) -> RemovalResponse:
    return RemovalResponse(
        status=delete_record(db, DNSRecordIdentifier(zone_id=zone_id, name=record_name, type=record_type), user)
    )
