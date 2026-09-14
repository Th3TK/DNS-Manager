import logging
from typing import cast

from app.config import ENV_CONFIG
from app.management.dns.record import cleanup_record_metadata, create_record, delete_record, get_record, modify_record
from app.management.dns.validation import is_record_name_in_zone
from app.management.trash.trash import delete_trash_entry, find_trashed_record
from app.models.record import CreateDNSRecordArgs, DNSRecord, ModifyDNSRecordArgs
from app.providers.factory import provider
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def watcher_update(db: Session, record_name: str, content: str, watcher_name: str):
    zone_name = ENV_CONFIG.MANAGED_ZONE

    # remove metadata for records within the zone that were deleted outside of the application
    # to ensure there won't be fake duplicates
    cleanup_record_metadata(db, zone_name)

    if not is_record_name_in_zone(record_name, zone_name):
        logger.warning(
            "Watcher %s tried to create a record %s outside of the managed zone %s",
            record_name,
            zone_name,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DNS record name is out of the managed zone.",
        )

    # get all records of the same name regardless of zone
    duplicate = provider.get_record(zone_name, record_name, "A")

    # doesn't exist
    if duplicate is None:
        matching_trash_entries = find_trashed_record(db, zone_name, record_name, "A")

        for entry in matching_trash_entries:
            record = cast(DNSRecord, entry.object_data)

            # different content
            if isinstance(record.content, str) and record.content != content:
                continue

            # different content
            if content not in record.content:
                continue

            # if trash entry with matching content was found, restore it:
            create_record(
                db=db,
                creation_args=CreateDNSRecordArgs(
                    **record.model_dump(exclude={"author", "origin"}),
                    author=f"watcher:{watcher_name}",
                    origin="automatic => traefik",
                ),
                is_restoration=True,
            )

            delete_trash_entry(db, entry.entry_uuid, f"watcher:{watcher_name}")
            return

        return create_record(
            db=db,
            creation_args=CreateDNSRecordArgs(
                zone_name=zone_name,
                name=record_name,
                type="A",
                content=content,
                ttl=60,
                author=f"watcher:{watcher_name}",
                origin="automatic => traefik",
            ),
        )

    # same content
    if isinstance(duplicate.content, str) and duplicate.content == content:
        return

    # same content
    if content in duplicate.content:
        return

    # same (name, type), different content
    modify_record(
        db=db,
        zone_name=zone_name,
        name=record_name,
        type_="A",
        modification_args=ModifyDNSRecordArgs(
            content=content,
            ttl=60,
            author=f"watcher:{watcher_name}",
            origin="automatic => traefik",
        ),
    )


def watcher_delete(db: Session, record_name: str, content: str, watcher_name: str):
    zone_name = ENV_CONFIG.MANAGED_ZONE

    if not is_record_name_in_zone(record_name, zone_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DNS record name is out of the managed zone.",
        )

    try:
        record = get_record(db, zone_name, record_name, "A")
    except HTTPException as exc:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            return
        raise

    if isinstance(record.content, str) and record.content != content:
        return

    if content not in record.content:
        return

    delete_record(db, zone_name, record_name, "A", f"watcher:{watcher_name}")
