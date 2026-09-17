import logging
from typing import cast

from app.config import ENV_CONFIG
from app.management.dns.record import (
    create_record,
    delete_record,
    get_record,
    get_records,
    has_matching_content,
    modify_record,
)
from app.management.dns.validation import is_record_name_in_zone
from app.management.trash.restore import restore_trash_entry
from app.management.trash.trash import find_trashed_record
from app.models.record import CreateDNSRecordArgs, DNSRecord, ModifyDNSRecordArgs
from app.providers.factory import provider
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def watcher_update(db: Session, record_name: str, content: str, watcher_name: str) -> None:
    """
    Updates an A record based on the provided name and content.

    - Does nothing if the record already has the matching content (author and origin stay unchanged).
    - Updates an existing record if the name matches.
    - Otherwise, restores a matching record from trash if available.
    - Otherwise, creates a new record.

    Updated or restored records have author `watcher:watcher_name` and origin `automatic => traefik`.
    """

    zone_name = ENV_CONFIG.MANAGED_ZONE

    if zone_name is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DNS record name is out of the managed zone.",
        )

    if not is_record_name_in_zone(record_name, zone_name):
        logger.warning(
            "Watcher %s tried to create a record %s outside of the managed zone %s",
            watcher_name,
            record_name,
            zone_name,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DNS record name is out of the managed zone.",
        )

    # find existing record
    duplicate = provider.get_record(zone_name, record_name, "A")

    # exists
    if duplicate is not None:
        # same content
        if has_matching_content(duplicate, content):
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
                comment="",
                checks_enabled=True,
            ),
            is_watcher_modification=True,
        )
        return None

    # does not exist

    # find matching trash entry
    matching_trash_entries = find_trashed_record(db, zone_name, record_name, "A")
    matching_content_entry = next(
        (entry for entry in matching_trash_entries if has_matching_content(cast(DNSRecord, entry.object_data), content)),
        None,
    )

    if matching_content_entry:
        restore_trash_entry(
            db=db,
            entry_uuid=matching_content_entry.entry_uuid,
            actor=f"watcher:{watcher_name}",
            origin="automatic => traefik",
        )
    else:
        create_record(
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


def watcher_delete(db: Session, record_name: str, content: str, watcher_name: str) -> None:
    """
    Deletes an A record with matching (`record_name`, `content`) and origin = `automatic => traefik`.
    """

    zone_name = ENV_CONFIG.MANAGED_ZONE

    if zone_name is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DNS record name is out of the managed zone.",
        )

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

    if not has_matching_content(record, content):
        return

    if record.origin != "automatic => traefik":
        return

    delete_record(db, zone_name, record_name, "A", f"watcher:{watcher_name}")


def watcher_sync(db: Session, record_names: list[str], content: str, watcher_name: str):
    """
    Creates or updates records for the names in `record_names` using `content` using `watcher_update()`.
    All existing `A` records with author `watcher:watcher_name` not present in the `record_names` will get deleted.
    """

    zone_name = ENV_CONFIG.MANAGED_ZONE

    if zone_name is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DNS record name is out of the managed zone.",
        )

    record_names_set = set(record_names)
    author = f"watcher:{watcher_name}"

    records = get_records(db, zone_name)

    # remove all existing `A` records with matching author not present in the `record_names`
    for record in records:
        if (
            record.author != author
            or record.type != "A"
            or record.origin != "automatic => traefik"
            or record.name in record_names_set
        ):
            continue

        delete_record(db, zone_name, record.name, "A", f"watcher:{watcher_name}")

    # ensure all records from `record_names` get updated
    # watcher_update already handles exact (name, type, content) matches
    for record_name in record_names:
        try:
            watcher_update(db, record_name, content, watcher_name)
        except HTTPException as exc:
            logging.warning(f"HTTP exception during watcher:{watcher_name} synchronization: %s", str(exc))
