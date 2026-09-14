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
    DNSRecordProperties,
    DNSRecordRemovalResult,
    ModifyDNSRecordArgs,
    SupportedDNSRecordTypes,
)
from app.providers.factory import provider
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import CursorResult, delete, select, tuple_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def cleanup_record_metadata(db: Session, *zone_names: str):
    """
    Remove metadata for records that no longer exist in the provider
    including record metadata from non existent zones.
    (i.e. they were deleted outside of the application).
    """
    removed = 0

    for zone_name in zone_names:
        records = provider.get_records(zone_name) or []

        record_keys = {(record.name, record.type) for record in records}

        result = cast(
            CursorResult[Any],
            db.execute(
                delete(DNSRecordMetadataInDB).where(
                    DNSRecordMetadataInDB.zone_name == zone_name,
                    ~tuple_(
                        DNSRecordMetadataInDB.name,
                        DNSRecordMetadataInDB.type,
                    ).in_(record_keys),
                )
            ),
        )

        removed += result.rowcount

    db.commit()

    logger.info("Removed %d stale records from the database.", removed)


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


def expand_records_properties_with_metadata(db: Session, properties: list[DNSRecordProperties]) -> list[DNSRecord]:
    record_keys = {(record.zone_name, record.name, record.type) for record in properties}

    if not record_keys:
        return []

    metadata_by_key: dict[tuple[str, str, str], DNSRecordMetadataInDB] = {}

    record_keys = list(record_keys)

    for i in range(0, len(record_keys), 1000):
        batch = record_keys[i : i + 1000]

        metadata_records_in_db = db.scalars(
            select(DNSRecordMetadataInDB).where(
                tuple_(
                    DNSRecordMetadataInDB.zone_name,
                    DNSRecordMetadataInDB.name,
                    DNSRecordMetadataInDB.type,
                ).in_(batch)
            )
        )

        metadata_by_key.update(
            {(metadata.zone_name, metadata.name, metadata.type): metadata for metadata in metadata_records_in_db}
        )

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


def get_records(db: Session, zone_name: str) -> list[DNSRecord]:
    properties = provider.get_records(zone_name)

    if properties is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DNSZone with name='{zone_name}' could not be found.",
        )

    return expand_records_properties_with_metadata(db, properties)


def get_all_records(db: Session) -> list[DNSRecord]:
    properties = provider.query_records("*")

    metadata_records_in_db = db.scalars(select(DNSRecordMetadataInDB)).all()

    metadata_by_key = {
        (record_metadata.zone_name, record_metadata.name, record_metadata.type): record_metadata
        for record_metadata in metadata_records_in_db
    }

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


def validate_no_duplicate(zone_name: str, name: str, type_: str):
    """
    Raises HTTP 409 if record with provided (name, type) already exists.
    If duplicate is from a different zone than provided in `zone_name`, returns an according detail
    explaining that DNS records with the same name and type across zones are not allowed.
    """

    # querying records with the same name across zones
    records_with_equal_name = provider.query_records(name_query=name)
    # filtering out records of different type
    duplicate = next(
        (record for record in records_with_equal_name if record.type == type_),
        None,
    )

    if duplicate:
        detail = "DNS record with the same name and type already exists. "

        if duplicate.zone_name != zone_name:
            detail = detail + (
                f'An existing "{duplicate.type}" record named "{duplicate.name}" already exists in zone "{duplicate.zone_name}". '
                "DNS records with the same name and type across zones are not allowed to prevent unexpected errors."
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


def create_record(db: Session, creation_args: CreateDNSRecordArgs, is_restoration: bool = False) -> DNSRecord:
    """
    Creates a record in a zone.

    Raises HTTP 404 if zone doesn't exist in the provider.
    Raises HTTP 409 if another record with the same (name, type) already exists.
    Raises DNSValidationError if args are invalid.
    """

    # remove metadata for records within the zone that were deleted outside of the application
    # to ensure there won't be fake duplicates
    cleanup_record_metadata(db, creation_args.zone_name)

    validate_dns_record_name(creation_args.name, creation_args.zone_name)
    validate_record_content(creation_args.content, creation_args.type)

    zone = provider.get_zone(creation_args.zone_name)

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DNS zone with name='{creation_args.zone_name}' could not be found.",
        )

    # ensure there are no duplicate (name, type) records, even across zones
    validate_no_duplicate(creation_args.zone_name, creation_args.name, creation_args.type)

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
        origin=creation_args.origin,
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


def modify_record(
    db: Session, zone_name: str, name: str, type_: SupportedDNSRecordTypes, modification_args: ModifyDNSRecordArgs
) -> DNSRecord:
    """
    Modifies record properties.

    Raises HTTP 400 if record is external (no database metadata found).
    Raises HTTP 404 if zone doesn't exist in the provider.
    Raises HTTP 409 when modifying record's name and/or type, and if another record with the same key already exists.
    Raises DNSValidationError if args are invalid.
    """

    # remove metadata for records within the zone that were deleted outside of the application
    # to ensure there won't be fake duplicates
    cleanup_record_metadata(db, zone_name)

    # validate query
    validate_dns_record_name(name, zone_name)

    # validate new name
    if modification_args.name:
        validate_dns_record_name(modification_args.name, zone_name)

    # validate content
    if modification_args.content:
        validate_record_content(modification_args.content, modification_args.type or type_)

    properties_old = provider.get_record(zone_name, name, type_)

    # check if zone and record exists
    if properties_old is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"DNS record with zone_id='{zone_name}', name='{name}', type='{type_}' could not be found."),
        )

    # get the ORM object from the database
    record_metadata_in_db = db.scalar(
        select(DNSRecordMetadataInDB).where(
            DNSRecordMetadataInDB.zone_name == zone_name,
            DNSRecordMetadataInDB.name == name,
            DNSRecordMetadataInDB.type == type_,
        )
    )

    # validate origin
    if not record_metadata_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The API does not support modifying DNS records created outside the application.",
        )

    updates = modification_args.model_dump(exclude_unset=True)

    record_old = DNSRecord(**properties_old.model_dump(), **DNSRecordMetadata.from_db(record_metadata_in_db).model_dump())

    record_new = DNSRecord(
        **{
            **record_old.model_dump(),
            **updates,
            "author": modification_args.author,
            "origin": modification_args.origin,
        }
    )

    # if there are no changes to be made, return
    if record_old == record_new:
        return record_old

    # if we're modifying name or type, then check for existing duplicates
    if record_old.name != record_new.name or record_old.type != record_new.type:
        validate_no_duplicate(record_new.zone_name, record_new.name, record_new.type)

    # modify record in the DNS provider
    properties = provider.modify_record(
        zone_name=zone_name,
        name=name,
        type_=type_,
        new_name=record_new.name,
        new_type=record_new.type,
        new_ttl=record_new.ttl,
        new_content=str(record_new.content),
    )

    # modify the metadata ORM object
    record_metadata_in_db.name = record_new.name
    record_metadata_in_db.type = record_new.type
    record_metadata_in_db.comment = record_new.comment
    record_metadata_in_db.checks_enabled = record_new.checks_enabled
    record_metadata_in_db.author = record_new.author
    record_metadata_in_db.origin = modification_args.origin  # type: ignore

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to save metadata for DNS record %s %s %s.", properties.name, properties.type, properties.content)

    create_log_entry(
        db=db,
        actor_type=ActorType.USER,
        actor=modification_args.author,
        action=ChangeAction.CHANGED,
        affected_object_type=DNSObjectType.RECORD,
        affected_object_name=record_old.name,
        object_before=jsonable_encoder(record_old),
        object_after=jsonable_encoder(record_new),
    )

    return record_new


def delete_record(db: Session, zone_name: str, name: str, type_: str, actor: str) -> DNSRecordRemovalResult:
    """
    Deletes a record. Internal records are soft-deleted and stored in the trash. External records are permanently deleted.
    """

    record = get_record(db, zone_name, name, type_)

    is_record_external = record.origin == "external"

    # delete the record from the DNS provider
    provider.delete_record(zone_name, name, type_)

    result = DNSRecordRemovalResult(record_status=ChangeAction.PERMANENTLY_DELETED)

    if not is_record_external:
        # try creating a trash entry
        if create_trash_entry(db=db, actor=actor, object_type=DNSObjectType.RECORD, object_data=record):
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
        actor,
        result.record_status.replace("_", " "),
        zone_name,
        name,
        type_,
    )

    create_log_entry(
        db=db,
        actor_type=ActorType.USER,
        actor=actor,
        action=result.record_status,
        affected_object_type=DNSObjectType.RECORD,
        affected_object_name=record.name,
        object_before=jsonable_encoder(record),
        object_after=None,
    )

    return result
