from uuid import UUID

from app.database.models.dns_trash import DNSTrashInDB
from app.database.models.enums import DNSObjectType
from app.management.dns.record import create_record
from app.management.dns.zone import create_zone
from app.models.record import CreateDNSRecordArgs, DNSRecord, DNSRecordOriginInternal
from app.models.trash import TrashEntry
from app.models.zone import CreateDNSZoneArgs, DNSZone
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session


def restore_trash_entry(
    db: Session, entry_uuid: UUID, actor: str, origin: DNSRecordOriginInternal = "manual"
) -> DNSZone | DNSRecord:

    trash_entry_in_db = db.scalar(select(DNSTrashInDB).where(DNSTrashInDB.entry_uuid == entry_uuid))

    if trash_entry_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trash entry with entry_uuid='{entry_uuid}' could not be found.",
        )

    trash_entry = TrashEntry.from_db(trash_entry_in_db)

    match trash_entry.object_type:
        case DNSObjectType.ZONE:
            response = create_zone(
                db=db,
                creation_args=CreateDNSZoneArgs(
                    **trash_entry.object_data.model_dump(exclude={"author"}),
                    author=actor,
                ),
                is_restoration=True,
            )
        case DNSObjectType.RECORD:
            response = create_record(
                db=db,
                creation_args=CreateDNSRecordArgs(
                    **trash_entry.object_data.model_dump(exclude={"author", "origin"}),
                    author=actor,
                    origin=origin,
                ),
                is_restoration=True,
            )

    db.delete(trash_entry_in_db)
    db.commit()

    return response
