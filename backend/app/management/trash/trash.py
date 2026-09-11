import logging
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from app.database.models.dns_trash import DNSTrashInDB
from app.database.models.enums import ActorType, ChangeAction, DNSObjectType
from app.management.action_log.action_log import create_log_entry
from app.management.trash.cleanup import automatic_trash_removal
from app.models.record import DNSRecord
from app.models.trash import TrashEntry
from app.models.user import User
from app.models.zone import DNSZone
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_trash_entries_query(
    db: Session,
    deletion_timestamp_min: int | None,
    deletion_timestamp_max: int | None,
    actor: str | None,
    object_type: DNSObjectType | None,
    sort_by: Literal["deletion_timestamp", "actor", "object_type"],
    sort_order: Literal["ascend", "descend"],
) -> Select:
    """
    Prepares a query for paginated, filtered and sorted retrieval of trash entries from the database.
    """

    query = select(DNSTrashInDB)

    if deletion_timestamp_min is not None:
        query = query.where(
            DNSTrashInDB.deletion_timestamp > datetime.fromtimestamp(deletion_timestamp_min / 1000, tz=timezone.utc)
        )

    if deletion_timestamp_max is not None:
        query = query.where(
            DNSTrashInDB.deletion_timestamp < datetime.fromtimestamp(deletion_timestamp_max / 1000, tz=timezone.utc)
        )

    if actor is not None:
        query = query.where(DNSTrashInDB.actor == actor)

    if object_type is not None:
        query = query.where(DNSTrashInDB.object_type == object_type)

    if sort_by is not None and sort_order is not None:
        col = getattr(DNSTrashInDB, sort_by)
        query = query.order_by(col.asc() if sort_order == "ascend" else col.desc())

    return query


def get_trash_entry(db: Session, entry_uuid: UUID) -> TrashEntry:
    """
    Retrieves a single trash entry from the database.
    """

    trash_entry_in_db = db.scalar(select(DNSTrashInDB).where(DNSTrashInDB.entry_uuid == entry_uuid))

    if trash_entry_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash entry with entry_uuid='{entry_uuid}' could not be found.",
        )

    return TrashEntry.from_db(trash_entry_in_db)


def create_trash_entry(db: Session, actor: str, object_type: DNSObjectType, object_data: DNSRecord | DNSZone) -> bool:
    """
    Creates an entry in the dns_trash table, saving the object for possible restoration
    before its pernament deletion.

    Returns boolean indicating whether the operation was successful
    """

    trash_entry = DNSTrashInDB(
        actor=actor,
        object_type=object_type,
        object_data=jsonable_encoder(object_data),
    )

    try:
        db.add(trash_entry)
        db.commit()
    except Exception:
        db.rollback()
        logger.critical(
            "Failed to create a trash entry for the %s %s.",
            object_type,
            object_data,
            object_type,
        )
        return False

    # IMPORTANT - ensure that the trash removal loop is running
    automatic_trash_removal.start()
    return True


def create_trash_entries(
    db: Session, actor: str, object_type: DNSObjectType, objects_data: list[DNSRecord] | list[DNSZone]
) -> bool:
    """
    Creates entries in the dns_trash table, saving the deleted objects for possible restoration
    before its pernament deletion.

    Returns boolean indicating whether the operation was successful
    """

    if not objects_data:
        return True

    trash_entries = [
        DNSTrashInDB(
            actor=actor,
            object_type=object_type,
            object_data=jsonable_encoder(object_data),
        )
        for object_data in objects_data
    ]

    try:
        db.add_all(trash_entries)
        db.commit()
    except Exception:
        db.rollback()
        logger.critical(
            "Failed to create trash entries for the %s %s.",
            object_type,
            objects_data,
        )
        return False

    # IMPORTANT - ensure that the trash removal loop is running
    automatic_trash_removal.start()
    return True


def delete_trash_entry(db: Session, entry_uuid: UUID, logged_in_user: User) -> None:
    """
    Permanently removes a trash entry from the database.
    """

    trash_entry_in_db = db.get(DNSTrashInDB, entry_uuid)

    if trash_entry_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash entry with entry_uuid='{entry_uuid}' could not be found.",
        )

    trash_entry = TrashEntry.from_db(trash_entry_in_db)

    create_log_entry(
        db,
        actor_type=ActorType.USER,
        actor=logged_in_user.username,
        action=ChangeAction.PERMANENTLY_DELETED,
        affected_object_type=trash_entry.object_type,
        affected_object_name=trash_entry.object_data.name,
        object_before=jsonable_encoder(trash_entry.object_data),
        object_after=None,
    )

    db.delete(trash_entry_in_db)
    db.commit()
