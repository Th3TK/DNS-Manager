import logging

from app.database.models.action_log import ActionLogInDB
from app.database.models.dns_zone_metadata import DNSZoneMetadataInDB
from app.database.models.enums import ActionObjectType, ActorType, ChangeAction
from app.dns.factory import provider
from app.dns.models.zone import CreateDNSZoneArgs, DNSZone, DNSZoneMetadata
from app.dns.validators.base import validate_dns_name
from app.users.models.user import User
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def cleanup_zone_metadata(db: Session) -> None:
    """
    # Remove metadata for zones that no longer exist in the provider
    # (i.e. they were deleted outside of the application).
    """

    properties = provider.get_zones()

    zone_names = {zone.name for zone in properties}

    db.execute(delete(DNSZoneMetadataInDB).where(~DNSZoneMetadataInDB.name.in_(zone_names)))
    db.commit()


def get_zone(db: Session, zone_id: str) -> DNSZone | None:
    properties = provider.get_zone(zone_id)

    if properties is None:
        return None

    metadata_db = db.scalar(select(DNSZoneMetadataInDB).where(DNSZoneMetadataInDB.name == zone_id))

    metadata = DNSZoneMetadata.from_db(metadata_db)

    return DNSZone(**properties.model_dump(), **metadata.model_dump())


def get_zones(db: Session) -> list[DNSZone]:
    properties = provider.get_zones()

    zone_ids = {zone.id for zone in properties}

    if not zone_ids:
        return []

    metadata_records = db.scalars(select(DNSZoneMetadataInDB).where(DNSZoneMetadataInDB.id.in_(zone_ids))).all()

    metadata_by_id = {metadata.id: metadata for metadata in metadata_records}

    zones = []

    for zone_properties in properties:
        metadata = DNSZoneMetadata.from_db(metadata_by_id.get(zone_properties.id))

        zones.append(
            DNSZone(
                **zone_properties.model_dump(),
                **metadata.model_dump(),
            )
        )

    return zones


def create_zone(db: Session, creation_args: CreateDNSZoneArgs, logged_in_user: User) -> DNSZone:

    # remove metadata for zones that were deleted outside of the application
    cleanup_zone_metadata(db)

    validate_dns_name(creation_args.name)

    properties = provider.create_zone(creation_args)

    logger.info(f"{logged_in_user} created DNS zone {properties.id}")

    metadata = DNSZoneMetadataInDB(
        id=properties.id,
        name=properties.name,
        comment=creation_args.comment,
        author=creation_args.author,
    )

    log = ActionLogInDB(
        actor_type=ActorType.USER,
        actor=logged_in_user.username,
        action=ChangeAction.CREATED,
        affected_object_type=ActionObjectType.ZONE,
        object_before=None,
        object_after=DNSZone(
            id=properties.id,
            name=properties.name,
            author=logged_in_user.username,
            comment=creation_args.comment,
            origin="manual",
        ),
    )

    try:
        db.add(metadata)
        db.commit()
    except Exception:
        db.rollback()

        logger.exception(f"Failed to save metadata for DNS zone {properties.name}.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred while saving the zone metadata.",
        )

    try:
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

        logger.exception(f"Failed to save the action log for DNS zone {properties.name} creation.")

    return DNSZone(
        **properties.model_dump(),
        origin="manual",
        author=metadata.author,
        comment=metadata.comment,
    )
