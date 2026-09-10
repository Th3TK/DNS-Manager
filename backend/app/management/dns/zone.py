import logging
from typing import Any, cast

from app.database.models.dns_record_metadata import DNSRecordMetadataInDB
from app.database.models.dns_zone_metadata import DNSZoneMetadataInDB
from app.database.models.enums import ActorType, ChangeAction, DNSObjectType
from app.management.action_log.action_log import create_log_entries, create_log_entry
from app.management.dns.record import get_records
from app.management.dns.validation import validate_dns_name
from app.management.trash.trash import create_trash_entries, create_trash_entry
from app.models.user import User
from app.models.zone import CreateDNSZoneArgs, DNSZone, DNSZoneMetadata, DNSZoneRemovalResult
from app.providers.factory import provider
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import CursorResult, delete, select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def cleanup_zone_metadata(db: Session):
    """
    # Remove metadata for zones that no longer exist in the provider
    # (i.e. they were deleted outside of the application).
    """

    zones = provider.get_zones(skip_record_count=True)

    zone_names = {zone.name for zone in zones}

    result = cast(CursorResult[Any], db.execute(delete(DNSZoneMetadataInDB).where(~DNSZoneMetadataInDB.name.in_(zone_names))))
    db.commit()

    logger.info("Removed %d stale zones from the database.", result.rowcount)


def get_zone(db: Session, zone_name: str) -> DNSZone:
    properties = provider.get_zone(zone_name)

    if properties is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"DNS zone with name='{zone_name}' could not be found.")

    metadata_in_db = db.scalar(select(DNSZoneMetadataInDB).where(DNSZoneMetadataInDB.name == zone_name))

    metadata = DNSZoneMetadata.from_db(metadata_in_db)

    return DNSZone(**properties.model_dump(), **metadata.model_dump())


def get_zones(db: Session, skip_record_count: bool = False) -> list[DNSZone]:
    properties = provider.get_zones(skip_record_count)

    zone_names = {zone.name for zone in properties}

    if not zone_names:
        return []

    metadata_zones_in_db = db.scalars(select(DNSZoneMetadataInDB).where(DNSZoneMetadataInDB.name.in_(zone_names))).all()

    metadata_by_name = {metadata.name: metadata for metadata in metadata_zones_in_db}

    zones = []

    for zone_properties in properties:
        zone_metadata = DNSZoneMetadata.from_db(metadata_by_name.get(zone_properties.name))

        zones.append(
            DNSZone(
                **zone_properties.model_dump(),
                **zone_metadata.model_dump(),
            )
        )

    return zones


def create_zone(db: Session, creation_args: CreateDNSZoneArgs, is_restoration: bool = False) -> DNSZone:

    # remove metadata for zones that were deleted outside of the application
    cleanup_zone_metadata(db)

    validate_dns_name(creation_args.name)

    properties = provider.create_zone(zone_name=creation_args.name)

    logger.info("%s created DNS zone %s", creation_args.author, properties.name)

    metadata = DNSZoneMetadataInDB(
        name=properties.name,
        comment=creation_args.comment,
        author=creation_args.author,
    )

    zone = DNSZone(
        **properties.model_dump(),
        **DNSZoneMetadata.from_db(metadata).model_dump(),
    )

    try:
        db.add(metadata)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to save metadata for DNS zone %s.", properties.name)
        zone = DNSZone(**properties.model_dump(), **DNSZoneMetadata.from_db(None).model_dump())

    create_log_entry(
        db=db,
        actor_type=ActorType.USER,
        actor=creation_args.author,
        action=(ChangeAction.RESTORED if is_restoration else ChangeAction.CREATED),
        affected_object_type=DNSObjectType.ZONE,
        affected_object_name=zone.name,
        object_before=None,
        object_after=jsonable_encoder(zone),
    )

    return zone


def delete_zone(db: Session, zone_name: str, logged_in_user: User) -> DNSZoneRemovalResult:
    """
    Deletes a DNS zone and all of its records.

    Internal zones are soft-deleted and stored in the trash. Records belonging to internal
    zones are also stored in the trash. External zones are permanently deleted.

    Returns a DNSZoneRemovalResult indicating whether the zone and its internal records
    were soft-deleted or permanently deleted.
    """
    zone = get_zone(db, zone_name)

    records = get_records(db, zone_name)
    internal_records, external_records = [], []

    for record in records:
        if record.origin == "external":
            external_records.append(record)
        else:
            internal_records.append(record)

    # delete zone and all its records from the DNS provider
    provider.delete_zone(zone_name)

    result = DNSZoneRemovalResult(
        zone_status=ChangeAction.PERMANENTLY_DELETED,
        internal_records_status=ChangeAction.PERMANENTLY_DELETED,
    )

    if create_trash_entry(
        db=db,
        actor=logged_in_user.username,
        object_type=DNSObjectType.ZONE,
        object_data=zone,
    ):
        result.zone_status = ChangeAction.DELETED

    if create_trash_entries(
        db=db,
        actor=logged_in_user.username,
        object_type=DNSObjectType.RECORD,
        objects_data=internal_records,
    ):
        result.internal_records_status = ChangeAction.DELETED

    try:
        # deletes the zone metadata and records metadata
        db.execute(delete(DNSZoneMetadataInDB).where(DNSZoneMetadataInDB.name == zone_name))
        db.execute(delete(DNSRecordMetadataInDB).where(DNSRecordMetadataInDB.zone_name == zone_name))
        db.commit()

    except Exception:
        db.rollback()
        logger.exception("Failed to delete stale metadata for the deleted DNS zone %s.", zone_name)

    logger.info("%s %s DNS zone %s", logged_in_user.username, result.zone_status.replace("_", " "), zone.name)

    create_log_entry(
        db=db,
        actor_type=ActorType.USER,
        actor=logged_in_user.username,
        action=result.zone_status,
        affected_object_type=DNSObjectType.ZONE,
        affected_object_name=zone.name,
        object_before=jsonable_encoder(zone),
        object_after=None,
    )

    create_log_entries(
        db=db,
        actor_type=ActorType.USER,
        actor=logged_in_user.username,
        action=ChangeAction.PERMANENTLY_DELETED,
        affected_object_type=DNSObjectType.RECORD,
        affected_object_names=[record.name for record in external_records],
        objects_before=jsonable_encoder(external_records),
        objects_after=None,
    )

    if internal_records:
        create_log_entries(
            db=db,
            actor_type=ActorType.USER,
            actor=logged_in_user.username,
            action=result.internal_records_status,
            affected_object_type=DNSObjectType.RECORD,
            affected_object_names=[record.name for record in external_records],
            objects_before=jsonable_encoder(internal_records),
            objects_after=None,
        )

    return result
