import logging
from typing import Any, cast

from app.database.models.dns_record_metadata import DNSRecordMetadataInDB
from app.database.models.enums import ActorType, ChangeAction, DNSObjectType
from app.management.action_log.action_log import create_log_entry
from app.management.dns.validation import validate_dns_record_name, validate_record_content
from app.management.trash.trash import create_trash_entry
from app.models.record import (
    CreateDNSRecordArgs,
    DNSRecord,
    DNSRecordMetadata,
    DNSRecordRemovalResult,
    ModifyDNSRecordArgs,
    RestoreDNSRecordArgs,
)
from app.models.user import User
from app.providers.factory import provider
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import CursorResult, delete, select, tuple_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def cleanup_record_metadata(db: Session, *zone_names: str) -> int:
    """
    Remove metadata for records that no longer exist in the provider
    (i.e. they were deleted outside of the application).
    """
    record_keys: set[tuple[str, str, str]] = set()

    for zone_name in zone_names:
        records = provider.get_records(zone_name) or []

        record_keys.update((zone_name, record.name, record.type) for record in records)

    result = cast(
        CursorResult[Any],
        db.execute(
            delete(DNSRecordMetadataInDB).where(
                ~tuple_(
                    DNSRecordMetadataInDB.zone_name,
                    DNSRecordMetadataInDB.name,
                    DNSRecordMetadataInDB.type,
                ).in_(record_keys),
            )
        ),
    )

    db.commit()

    return result.rowcount


def get_record(db: Session, zone_name: str, name: str, type_: str) -> DNSRecord:
    properties = provider.get_record(zone_name, name, type_)

    if properties is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"DNS record with zone_id='{zone_name}', name='{name}', type='{type_}' could not be found."),
        )

    metadata_in_db = db.scalar(
        select(DNSRecordMetadataInDB).where(
            DNSRecordMetadataInDB.zone_name == zone_name,
            DNSRecordMetadataInDB.name == name,
            DNSRecordMetadataInDB.type == type_,
        )
    )

    metadata = DNSRecordMetadata.from_db(metadata_in_db)

    return DNSRecord(**properties.model_dump(), **metadata.model_dump())


def get_records(db: Session, zone_name: str) -> list[DNSRecord]:
    properties = provider.get_records(zone_name)

    if properties is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DNSZone with name='{zone_name}' could not be found.",
        )

    record_keys = {(record.zone_name, record.name, record.type) for record in properties}

    if not record_keys:
        return []

    metadata_records_in_db = db.scalars(
        select(DNSRecordMetadataInDB).where(
            tuple_(
                DNSRecordMetadataInDB.zone_name,
                DNSRecordMetadataInDB.name,
                DNSRecordMetadataInDB.type,
            ).in_(record_keys)
        )
    )

    metadata_by_key = {(metadata.zone_name, metadata.name, metadata.type): metadata for metadata in metadata_records_in_db}

    records = []

    for record_properties in properties:
        record_metadata = DNSRecordMetadata.from_db(
            metadata_by_key.get((record_properties.zone_name, record_properties.name, record_properties.type))
        )

        records.append(
            DNSRecord(
                **record_properties.model_dump(),
                **record_metadata.model_dump(),
            )
        )

    return records


def create_record(db: Session, creation_args: CreateDNSRecordArgs, is_restoration: bool = False) -> DNSRecord:
    # remove metadata for records within the zone that were deleted outside of the application
    cleanup_record_metadata(db, creation_args.zone_name)

    validate_dns_record_name(creation_args.name, creation_args.zone_name)
    validate_record_content(creation_args.content, creation_args.type)

    # the API does not allow creating records with the same (name, type) key
    duplicate = provider.get_record(
        zone_name=creation_args.zone_name,
        name=creation_args.name,
        type_=creation_args.type,
    )

    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="DNS record with the same name and type already exists.",
        )

    zone = provider.get_zone(creation_args.zone_name)

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DNS zone with name='{creation_args.zone_name}' could not be found.",
        )

    properties = provider.create_record(
        zone_name=creation_args.zone_name,
        name=creation_args.name,
        type_=creation_args.type,
        content=creation_args.content,
        ttl=creation_args.ttl,
    )

    logger.info("%s created DNS record %s %s %s", creation_args.author, properties.name, properties.type, properties.content)

    metadata = DNSRecordMetadataInDB(
        zone_name=creation_args.zone_name,
        name=creation_args.name,
        type=creation_args.type,
        comment=creation_args.comment,
        checks_enabled=creation_args.checks_enabled,
        author=creation_args.author,
        origin="manual",
    )

    record = DNSRecord(**properties.model_dump(), **DNSRecordMetadata.from_db(metadata).model_dump())

    try:
        db.add(metadata)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception(
            "Failed to save metadata for DNS record  %s %s %s.", properties.name, properties.type, properties.content
        )
        record = DNSRecord(**properties.model_dump(), **DNSRecordMetadata.from_db(None).model_dump())

    create_log_entry(
        db=db,
        actor_type=ActorType.USER,
        actor=creation_args.author,
        action=(ChangeAction.RESTORED if is_restoration else ChangeAction.CREATED),
        affected_object_type=DNSObjectType.RECORD,
        affected_object_name=record.name,
        object_before=None,
        object_after=jsonable_encoder(record),
    )

    return record


def modify_record(db: Session, modification_args: ModifyDNSRecordArgs) -> DNSRecord:
    # remove metadata for records within the zone that were deleted outside of the applicationd
    cleanup_record_metadata(db, modification_args.zone_name)

    validate_dns_record_name(modification_args.name, modification_args.zone_name)
    validate_record_content(modification_args.content, modification_args.type)

    # get the existing record; raises 404 if it does not exist.
    record_old: DNSRecord = get_record(db, modification_args.zone_name, modification_args.name, modification_args.type)

    # get the ORM object
    record_metadata_in_db = db.scalar(
        select(DNSRecordMetadataInDB).where(
            DNSRecordMetadataInDB.zone_name == modification_args.zone_name,
            DNSRecordMetadataInDB.name == modification_args.name,
            DNSRecordMetadataInDB.type == modification_args.type,
        )
    )

    if not record_metadata_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The API does not support modifying DNS records created outside the application.",
        )

    zone = provider.get_zone(modification_args.zone_name)

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DNSZone with name='{modification_args.zone_name}' could not be found.",
        )

    # provider DNS record modification
    properties = provider.modify_record(
        zone_name=modification_args.zone_name,
        name=modification_args.name,
        type_=modification_args.type,
        content=modification_args.content,
        ttl=modification_args.ttl,
    )

    # modify the metadata ORM object
    record_metadata_in_db.comment = modification_args.comment
    record_metadata_in_db.checks_enabled = modification_args.checks_enabled
    record_metadata_in_db.author = modification_args.author

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to save metadata for DNS record %s %s %s.", properties.name, properties.type, properties.content)

    metadata = DNSRecordMetadata.from_db(record_metadata_in_db)

    record = DNSRecord(**properties.model_dump(), **metadata.model_dump())

    create_log_entry(
        db=db,
        actor_type=ActorType.USER,
        actor=modification_args.author,
        action=ChangeAction.CHANGED,
        affected_object_type=DNSObjectType.RECORD,
        affected_object_name=record.name,
        object_before=jsonable_encoder(record_old),
        object_after=jsonable_encoder(record),
    )

    return record


def delete_record(db: Session, zone_name: str, name: str, type_: str, logged_in_user: User) -> DNSRecordRemovalResult:
    """
    Deletes a DNS zone and all of its records.

    Internal records are soft-deleted and stored in the trash. External records are permanently deleted.
    """

    record = get_record(db, zone_name, name, type_)

    is_record_external = record.origin == "external"

    # delete the record from the DNS provider
    provider.delete_record(zone_name, name, type_)

    result = DNSRecordRemovalResult(record_status=ChangeAction.PERMANENTLY_DELETED)

    if not is_record_external:
        if create_trash_entry(
            db=db,
            actor=logged_in_user.username,
            object_type=DNSObjectType.RECORD,
            object_data=RestoreDNSRecordArgs(**record.model_dump()),
        ):
            result.record_status = ChangeAction.DELETED

        try:
            db.execute(
                delete(DNSRecordMetadataInDB).where(
                    DNSRecordMetadataInDB.zone_name == zone_name,
                    DNSRecordMetadataInDB.name == name,
                    DNSRecordMetadataInDB.type == type_,
                )
            )
            db.commit()
        except Exception:
            db.rollback()
            logger.exception(
                "Failed to delete stale metadata for the deleted DNS record %s %s %s.",
                zone_name,
                name,
                type_,
            )

    logger.info(
        "%s %s DNS record %s %s %s",
        logged_in_user.username,
        result.record_status.replace("_", " "),
        zone_name,
        name,
        type_,
    )

    create_log_entry(
        db=db,
        actor_type=ActorType.USER,
        actor=logged_in_user.username,
        action=result.record_status,
        affected_object_type=DNSObjectType.RECORD,
        affected_object_name=record.name,
        object_before=jsonable_encoder(record),
        object_after=None,
    )

    return result
