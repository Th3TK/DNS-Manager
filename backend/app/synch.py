import logging

from fastapi import HTTPException, status
from sqlalchemy import select

from app.config import ENV_CONFIG
from app.database.connection import session_factory
from app.database.models.dns_record_metadata import DNSRecordMetadataInDB
from app.management.dns.record import cleanup_record_metadata
from app.management.dns.zone import cleanup_zone_metadata


def synchronize_database():
    """
    Removes outdated metadata entries from the database by quering the DNS provider for current data.
    """

    with session_factory() as db:
        logging.info("Synchronizing database metadata with DNS provider.")

        try:
            removed_zones: int = cleanup_zone_metadata(db)
            logging.info("Removed %d stale zones from the database.", removed_zones)

            zone_names = db.scalars(select(DNSRecordMetadataInDB.zone_name).distinct()).all()

            removed_records: int = cleanup_record_metadata(db, *zone_names)
            logging.info("Removed %d stale records from the database.", removed_records)
            logging.info("Database synchronization with the DNS provider completed.")

        except Exception as exc:
            logging.error("Database synchronization with the DNS provider FAILED.")

            if ENV_CONFIG.DNS_PROVIDER == "powerdns" and isinstance(exc, HTTPException):
                match exc.status_code:
                    case status.HTTP_401_UNAUTHORIZED:
                        logging.error(
                            "Database synchronization failed because PowerDNS rejected the request as unauthorized. "
                            "Ensure the POWERDNS_API_KEY environment variable is set correctly."
                        )
                    case status.HTTP_404_NOT_FOUND:
                        logging.error(
                            "Database synchronization failed because the PowerDNS API resource path was invalid. "
                            "Ensure the POWERDNS_API_URL and POWERDNS_SERVER_ID environment variables are set correctly."
                        )
