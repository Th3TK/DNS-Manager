import logging
from typing import Any, Literal, cast

from app.database.models.dns_zone_metadata import DNSZoneMetadataInDB
from app.database.models.enums import ActorType, ChangeAction, DNSObjectType
from app.dns.factory import provider
from app.dns.management.action_log import create_log_entry
from app.dns.management.trash import create_trash_entry
from app.dns.models.zone import CreateDNSZoneArgs, DNSZone, DNSZoneMetadata
from app.dns.validators.base import validate_dns_name
from app.users.models.user import User
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import CursorResult, delete, select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def cleanup_zone_metadata(db: Session) -> int:
    """
    # Remove metadata for zones that no longer exist in the provider
    # (i.e. they were deleted outside of the application).
    """

    zones = provider.get_zones()

    zone_names = {zone.name for zone in zones}

    result = cast(CursorResult[Any], db.execute(delete(DNSZoneMetadataInDB).where(~DNSZoneMetadataInDB.name.in_(zone_names))))
    db.commit()

    return result.rowcount


def get_zone(db: Session, zone_id: str) -> DNSZone:
    properties = provider.get_zone(zone_id)

    if properties is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"DNS zone with id='{zone_id}' could not be found.")

    metadata_in_db = db.scalar(select(DNSZoneMetadataInDB).where(DNSZoneMetadataInDB.name == zone_id))

    metadata = DNSZoneMetadata.from_db(metadata_in_db)

    return DNSZone(**properties.model_dump(), **metadata.model_dump())


def get_zones(db: Session) -> list[DNSZone]:
    properties = provider.get_zones()

    zone_ids = {zone.id for zone in properties}

    if not zone_ids:
        return []

    metadata_zones_in_db = db.scalars(select(DNSZoneMetadataInDB).where(DNSZoneMetadataInDB.id.in_(zone_ids))).all()

    metadata_by_id = {metadata.id: metadata for metadata in metadata_zones_in_db}

    zones = []

    for zone_properties in properties:
        zone_metadata = DNSZoneMetadata.from_db(metadata_by_id.get(zone_properties.id))

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

    properties = provider.create_zone(creation_args)

    logger.info("%s created DNS zone %s", creation_args.author, properties.id)

    metadata = DNSZoneMetadataInDB(
        id=properties.id,
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
        object_before=None,
        object_after=jsonable_encoder(zone),
    )

    return zone


def delete_zone(
    db: Session, zone_id: str, logged_in_user: User
) -> Literal[ChangeAction.PERMANENTLY_DELETED, ChangeAction.DELETED]:
    properties = provider.get_zone(zone_id)

    if properties is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"DNS zone with id='{zone_id}' could not be found.")

    provider.delete_zone(zone_id)

    logger.info("%s deleted DNS zone %s", logged_in_user.username, properties.id)

    metadata_in_db = db.scalar(select(DNSZoneMetadataInDB).where(DNSZoneMetadataInDB.id == zone_id))
    metadata = DNSZoneMetadata.from_db(metadata_in_db)

    deleted_zone = DNSZone(**properties.model_dump(), **metadata.model_dump())

    action = ChangeAction.PERMANENTLY_DELETED if metadata.origin == "external" else ChangeAction.DELETED

    if metadata.origin != "external":
        if not create_trash_entry(
            db,
            actor=logged_in_user.username,
            object_type=DNSObjectType.ZONE,
            object_data=CreateDNSZoneArgs(**deleted_zone.model_dump()),
        ):
            action = ChangeAction.PERMANENTLY_DELETED

        try:
            db.delete(metadata_in_db)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Failed to delete stale metadata for DNS zone %s.", properties.name)

    create_log_entry(
        db=db,
        actor_type=ActorType.USER,
        actor=logged_in_user.username,
        action=action,
        affected_object_type=DNSObjectType.ZONE,
        object_before=jsonable_encoder(deleted_zone),
        object_after=None,
    )

    return action
