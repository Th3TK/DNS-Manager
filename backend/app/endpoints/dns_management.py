import logging
from typing import Annotated

from app.database.database import get_db
from app.dns.management.zone import create_zone, get_zone, get_zones
from app.dns.models.record import CreateDNSRecordForm, DNSRecord
from app.dns.models.zone import CreateDNSZoneArgs, CreateDNSZoneForm, DNSZone
from app.users.authentication import get_authenticated_administrator, get_authenticated_user
from app.users.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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


@router.get("/zone", response_model=DNSZone)
def __get_singular_zone__(
    user: Annotated[User, Depends(get_authenticated_user)], db: Annotated[Session, Depends(get_db)], zone_id: str
) -> DNSZone:
    zone = get_zone(db, zone_id)

    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"DNS zone with id={zone_id} could not be found.")

    return zone


@router.post("/zone", response_model=DNSZone)
def __create_zone__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    form: CreateDNSZoneForm,
):
    return create_zone(
        db,
        CreateDNSZoneArgs(
            **form.model_dump(),
            author=user.username,
        ),
        user,
    )


@router.delete("/zone", response_model=None)
def __delete_zone__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    zone_id: str,
) -> None: ...


@router.get("/records", response_model=list[DNSRecord])
def __get_all_zone_records__(zone_id: str) -> list[DNSRecord]: ...


@router.get("/record", response_model=DNSRecord)
def __get_singular_record__(zone_id: str, record_name: str, type: str, content: str) -> DNSRecord: ...


@router.post("/record", response_model=DNSRecord)
def __create_record__(form: CreateDNSRecordForm) -> DNSRecord: ...
