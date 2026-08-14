
import logging

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import ENV_CONFIG
from app.database.models.dns_zone_metadata import DNSZoneMetadataInDB
from app.dns.models.dns_zone import CreateDNSZoneArgs, DNSZone, DNSZoneMetadata
from app.dns.providers.base import DNSProvider
from app.dns.providers.powerdns.adapter import PowerDNSAdapter
from app.dns.validators.base import validate_dns_name

logger = logging.getLogger(__name__)


def get_dns_provider() -> DNSProvider:
    match ENV_CONFIG.DNS_PROVIDER:
        case "powerdns":
            return PowerDNSAdapter()
        case _:
            logger.critical(
                "Invalid DNS provider configured: %r. The application cannot start and will now shut down.",
                ENV_CONFIG.DNS_PROVIDER,
            )
            raise SystemExit(1)
            
            
provider = get_dns_provider()


def cleanup_zone_metadata(db: Session) -> None:
    """
    # Remove metadata for zones that no longer exist in the provider
    # (i.e. they were deleted outside of the application).
    """    
    
    properties = provider.get_zones()
    
    zone_names = {zone.name for zone in properties}   
    
    db.execute(delete(DNSZoneMetadataInDB).where(~DNSZoneMetadataInDB.name.in_(zone_names)))
    db.commit()

    
def _create_zone_metadata_model(metadata_db: DNSZoneMetadataInDB | None) -> DNSZoneMetadata: 
    if metadata_db is None:
        return DNSZoneMetadata(origin="external")
    
    return DNSZoneMetadata(
        origin="manual",
        author=metadata_db.author,
        comment=metadata_db.comment,
    )


def get_zone(db: Session, zone_id: str) -> DNSZone:
    properties = provider.get_zone(zone_id)
    
    if properties is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'DNS zone with id={zone_id} could not be found.'
        )
    
    metadata_db = db.scalar(select(DNSZoneMetadataInDB).where(DNSZoneMetadataInDB.name == zone_id))
    
    metadata = _create_zone_metadata_model(metadata_db)
    
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
        metadata = _create_zone_metadata_model(metadata_by_id.get(zone_properties.id))

        zones.append(
            DNSZone(
                **zone_properties.model_dump(),
                **metadata.model_dump(),
            )
        )

    return zones
    
def create_zone(db: Session, creation_args: CreateDNSZoneArgs):
    validate_dns_name(creation_args.name)
    
    metadata = DNSZoneMetadataInDB(
        id=creation_args.name,
        name=creation_args.name,
        comment=creation_args.comment,
        author=creation_args.author,
    )
    
    try:
        db.add(metadata)
        db.flush()

        properties = provider.create_zone(creation_args)

        db.commit()

    except Exception:
        # If an exception occured during zone creation, remove the metadata from the db.
        db.rollback()
        raise

    return DNSZone(
        **properties.model_dump(),
        origin="manual",
        author=metadata.author,
        comment=metadata.comment,
    )
    
    