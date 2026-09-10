import logging
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models.enums import DNSObjectType
from app.management.dns.record import create_record
from app.management.dns.zone import create_zone
from app.management.trash.trash import delete_trash_entry, get_trash_entries_query, get_trash_entry
from app.management.users.authentication import get_authenticated_administrator, get_authenticated_user
from app.models.record import CreateDNSRecordArgs, DNSRecord
from app.models.trash import TrashEntry
from app.models.user import User
from app.models.zone import CreateDNSZoneArgs, DNSZone

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/trash",
    tags=["DNS Object Trash"],
)


@router.get("", response_model=Page[TrashEntry])
def __get_list_of_action_log_entries__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    deletion_timestamp_min: int | None = Query(None),
    deletion_timestamp_max: int | None = Query(None),
    actor: str | None = Query(None),
    object_type: DNSObjectType | None = Query(None),
    sort_by: Literal["deletion_timestamp", "actor", "object_type"] = Query("deletion_timestamp"),
    sort_order: Literal["ascend", "descend"] = Query("descend"),
) -> Page[TrashEntry]:
    query = get_trash_entries_query(
        db=db,
        deletion_timestamp_min=deletion_timestamp_min,
        deletion_timestamp_max=deletion_timestamp_max,
        actor=actor,
        object_type=object_type,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return paginate(db, query)


@router.get("/{entry_uuid}", response_model=TrashEntry)
def __get_action_log_entry__(
    user: Annotated[User, Depends(get_authenticated_user)], db: Annotated[Session, Depends(get_db)], entry_uuid: UUID
) -> TrashEntry:
    return get_trash_entry(db, entry_uuid)


@router.post("/restore/{entry_uuid}", response_model=DNSZone | DNSRecord, status_code=201)
def __restore_dns_object_from_trash__(
    user: Annotated[User, Depends(get_authenticated_administrator)], db: Annotated[Session, Depends(get_db)], entry_uuid: UUID
):
    trash_entry = get_trash_entry(db, entry_uuid)
    response = None

    match trash_entry.object_type:
        case DNSObjectType.ZONE:
            response = create_zone(
                db=db,
                creation_args=CreateDNSZoneArgs(
                    **trash_entry.object_data.model_dump(exclude={"author"}),
                    author=user.username,
                ),
                is_restoration=True,
            )
        case DNSObjectType.RECORD:
            response = create_record(
                db=db,
                creation_args=CreateDNSRecordArgs(
                    **trash_entry.object_data.model_dump(exclude={"author", "origin"}),
                    author=user.username,
                    origin="manual",
                ),
                is_restoration=True,
            )

    delete_trash_entry(db, entry_uuid, user)
    return response


@router.delete("/permanently-delete/{entry_uuid}", status_code=204)
def __permanently_delete_object_from_trash__(
    user: Annotated[User, Depends(get_authenticated_administrator)], db: Annotated[Session, Depends(get_db)], entry_uuid: UUID
) -> None:
    delete_trash_entry(db, entry_uuid, user)
