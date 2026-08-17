import logging

from app.database.models.action_log import ActionLogInDB
from app.database.models.dns_record_metadata import DNSRecordMetadataInDB
from app.database.models.enums import ActionObjectType, ActorType, ChangeAction
from app.dns.factory import provider
from app.dns.models.record import CreateDNSRecordArgs, DNSRecord, DNSRecordIdentifier, DNSRecordMetadata, ModifyDNSRecordArgs
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, select, tuple_
from sqlalchemy.orm import Session

from app.dns.validators.base import DNSValidationError, validate_dns_name, validate_dns_record_name
from app.dns.validators.record_content import validate_record_content

logger = logging.getLogger(__name__)


def cleanup_record_metadata(db: Session, zone_id: str) -> None:
    """
    Remove metadata for records that no longer exist in the provider
    (i.e. they were deleted outside of the application).
    """
    records = provider.get_records(zone_id)

    record_keys = {(record.name, record.type) for record in records}

    db.execute(
        delete(DNSRecordMetadataInDB).where(
            DNSRecordMetadataInDB.zone_id == zone_id,
            ~tuple_(
                DNSRecordMetadataInDB.name,
                DNSRecordMetadataInDB.type,
            ).in_(record_keys),
        )
    )
    db.commit()


def get_record(db: Session, record_id: DNSRecordIdentifier) -> DNSRecord:
    properties = provider.get_record(record_id)

    if properties is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "DNS record with "
                f"zone_id='{record_id.zone_id}', name='{record_id.name}', type='{record_id.type}' "
                "could not be found."
            ),
        )

    metadata_in_db = db.scalar(
        select(DNSRecordMetadataInDB).where(
            DNSRecordMetadataInDB.zone_id == record_id.zone_id,
            DNSRecordMetadataInDB.name == record_id.name,
            DNSRecordMetadataInDB.type == record_id.type,
        )
    )

    metadata = DNSRecordMetadata.from_db(metadata_in_db)

    return DNSRecord(**properties.model_dump(), **metadata.model_dump())


def get_records(db: Session, zone_id: str) -> list[DNSRecord]:
    properties = provider.get_records(zone_id)

    record_keys = {(record.zone_id, record.name, record.type) for record in properties}

    if not record_keys:
        return []

    metadata_records_in_db = db.scalars(
        select(DNSRecordMetadataInDB).where(
            tuple_(
                DNSRecordMetadataInDB.zone_id,
                DNSRecordMetadataInDB.name,
                DNSRecordMetadataInDB.type,
            ).in_(record_keys)
        )
    )

    metadata_by_key = {(metadata.zone_id, metadata.name, metadata.type): metadata for metadata in metadata_records_in_db}

    records = []

    for record_properties in properties:
        record_metadata = DNSRecordMetadata.from_db(
            metadata_by_key.get((record_properties.zone_id, record_properties.name, record_properties.type))
        )

        records.append(
            DNSRecord(
                **record_properties.model_dump(),
                **record_metadata.model_dump(),
            )
        )

    return records


def create_record(db: Session, creation_args: CreateDNSRecordArgs) -> DNSRecord:
    # remove metadata for records within the zone that were deleted outside of the application
    cleanup_record_metadata(db, creation_args.zone_id)

    try:
        validate_dns_record_name(creation_args.name, creation_args.zone_id)
        validate_record_content(creation_args.content, creation_args.type)
    except DNSValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    record_id = DNSRecordIdentifier.model_validate(creation_args.model_dump())

    # the API does not allow creating records with the same (name, type) key
    duplicate = provider.get_record(record_id)

    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="DNS record with the same name and type already exists.",
        )

    properties = provider.create_record(creation_args)

    logger.info(f"{creation_args.author} created DNS record {properties.name} {properties.type} {properties.content}")

    metadata = DNSRecordMetadataInDB(
        zone_id=creation_args.zone_id,
        name=creation_args.name,
        type=creation_args.type,
        comment=creation_args.comment,
        checks_enabled=creation_args.checks_enabled,
        author=creation_args.author,
        origin="manual",
    )

    record = DNSRecord(**properties.model_dump(), **DNSRecordMetadata.from_db(metadata).model_dump())

    log = ActionLogInDB(
        actor_type=ActorType.USER,
        actor=creation_args.author,
        action=ChangeAction.CREATED,
        affected_object_type=ActionObjectType.ZONE,
        object_before=None,
        object_after=jsonable_encoder(record),
    )

    try:
        db.add(metadata)
        db.commit()
    except Exception:
        db.rollback()

        logger.exception(f"Failed to save metadata for DNS record {properties.name} {properties.type} {properties.content}.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred while saving the record metadata.",
        )

    try:
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

        logger.exception(
            f"Failed to save the action log for DNS record {properties.name} {properties.type} {properties.content} creation."
        )

    return record


def modify_record(db: Session, modification_args: ModifyDNSRecordArgs) -> DNSRecord:
    # remove metadata for records within the zone that were deleted outside of the applicationd
    cleanup_record_metadata(db, modification_args.zone_id)

    try:
        validate_dns_record_name(modification_args.name, modification_args.zone_id)
        validate_record_content(modification_args.content, modification_args.type)
    except DNSValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    record_id = DNSRecordIdentifier.model_validate(modification_args.model_dump())

    # get the existing record; raises 404 if it does not exist.
    record_old: DNSRecord = get_record(db, record_id)

    # get the ORM object
    record_metadata_in_db = db.scalar(
        select(DNSRecordMetadataInDB).where(
            DNSRecordMetadataInDB.zone_id == record_id.zone_id,
            DNSRecordMetadataInDB.name == record_id.name,
            DNSRecordMetadataInDB.type == record_id.type,
        )
    )

    if not record_metadata_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The API does not support modifying DNS records created outside the application.",
        )

    # provider DNS record modification
    properties = provider.modify_record(modification_args)

    # modify the metadata ORM object
    record_metadata_in_db.comment = modification_args.comment
    record_metadata_in_db.checks_enabled = modification_args.checks_enabled
    record_metadata_in_db.author = modification_args.author

    try:
        db.commit()
    except Exception:
        db.rollback()

        logger.exception(f"Failed to save metadata for DNS record {properties.name} {properties.type} {properties.content}.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred while saving the record metadata.",
        )

    metadata = DNSRecordMetadata.from_db(record_metadata_in_db)

    record = DNSRecord(**properties.model_dump(), **metadata.model_dump())

    log = ActionLogInDB(
        actor_type=ActorType.USER,
        actor=modification_args.author,
        action=ChangeAction.CHANGED,
        affected_object_type=ActionObjectType.ZONE,
        object_before=jsonable_encoder(record_old),
        object_after=jsonable_encoder(record),
    )

    try:
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

        logger.exception(
            f"Failed to save the action log for DNS record {properties.name} {properties.type} {properties.content} modification."
        )

    return record
