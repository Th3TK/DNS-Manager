import logging

from app.database.models.dns_record_metadata import DNSRecordMetadataInDB
from app.dns.factory import provider
from app.dns.models.record import DNSRecord, DNSRecordIdentifier, DNSRecordMetadata
from fastapi import HTTPException, status
from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_record(db: Session, record_id: DNSRecordIdentifier) -> DNSRecord:
    properties = provider.get_record(record_id)

    if properties is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "DNS record with"
                f"zone_id={record_id.zone_id}, name={record_id.name}, type={record_id.type}, content={record_id.content}"
                "could not be found."
            ),
        )

    metadata_in_db = db.scalar(
        select(DNSRecordMetadataInDB).where(
            DNSRecordMetadataInDB.zone_id == record_id.zone_id,
            DNSRecordMetadataInDB.name == record_id.name,
            DNSRecordMetadataInDB.type == record_id.type,
            DNSRecordMetadataInDB.content == record_id.content,
        )
    )

    metadata = DNSRecordMetadata.from_db(metadata_in_db)

    return DNSRecord(**properties.model_dump(), **metadata.model_dump())


def get_records(db: Session, zone_id: str) -> list[DNSRecord]:
    properties = provider.get_records(zone_id)

    record_keys = {(record.zone_id, record.name, record.type, record.content) for record in properties}

    if not record_keys:
        return []

    metadata_records_in_db = db.scalars(
        select(DNSRecordMetadataInDB).where(
            tuple_(
                DNSRecordMetadataInDB.zone_id,
                DNSRecordMetadataInDB.name,
                DNSRecordMetadataInDB.type,
                DNSRecordMetadataInDB.content,
            ).in_(record_keys)
        )
    )

    metadata_by_key = {
        (metadata.zone_id, metadata.name, metadata.type, metadata.content): metadata for metadata in metadata_records_in_db
    }

    records = []

    for record_properties in properties:
        record_metadata = DNSRecordMetadata.from_db(
            metadata_by_key.get(
                (record_properties.zone_id, record_properties.name, record_properties.type, record_properties.content)
            )
        )

        records.append(
            DNSRecord(
                **record_properties.model_dump(),
                **record_metadata.model_dump(),
            )
        )

    return records
