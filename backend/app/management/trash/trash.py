import logging
from uuid import UUID

from app.database.models.dns_trash import DNSTrashInDB
from app.database.models.enums import DNSObjectType
from app.management.trash.cleanup import automatic_trash_removal
from app.models.record import CreateDNSRecordArgs
from app.models.trash import TrashEntry
from app.models.zone import CreateDNSZoneArgs
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_trash_entries(db: Session, limit: int = 100, offset=0) -> list[TrashEntry]:
    trash_entries_in_db = db.scalars(
        select(DNSTrashInDB).order_by(DNSTrashInDB.deletion_timestamp.asc()).offset(offset).limit(limit)
    )

    return [TrashEntry.from_db(trash_entry_in_db) for trash_entry_in_db in trash_entries_in_db]


def get_trash_entry(db: Session, entry_uuid: UUID) -> TrashEntry:
    trash_entry_in_db = db.scalar(select(DNSTrashInDB).where(DNSTrashInDB.entry_uuid == entry_uuid))

    if trash_entry_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash entry with entry_uuid='{entry_uuid}' could not be found.",
        )

    return TrashEntry.from_db(trash_entry_in_db)


def create_trash_entry(
    db: Session, actor: str, object_type: DNSObjectType, object_data: CreateDNSRecordArgs | CreateDNSZoneArgs
) -> bool:
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

    automatic_trash_removal.start()
    return True


def create_trash_entries(
    db: Session, actor: str, object_type: DNSObjectType, objects_data: list[CreateDNSRecordArgs] | list[CreateDNSZoneArgs]
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

    automatic_trash_removal.start()
    return True


def delete_trash_entry(db: Session, entry_uuid: UUID) -> None:
    trash_entry = db.get(DNSTrashInDB, entry_uuid)

    if trash_entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash entry with entry_uuid='{entry_uuid}' could not be found.",
        )

    db.delete(trash_entry)
    db.commit()
