import logging

from fastapi import HTTPException, status
from sqlalchemy import select

from app.config import ENV_CONFIG
from app.database.connection import session_factory
from app.database.models.dns_record_metadata import DNSRecordMetadataInDB
from app.management.dns.record import cleanup_record_metadata
from app.management.dns.zone import cleanup_zone_metadata
from app.management.users.users import create_user, get_active_admin_count
from app.models.user import CreateUserForm
from app.utils.env import get_env


def create_first_account():
    """
    Creates initial user if there are no active administrators in the users table is empty.
    """

    with session_factory() as db:
        logging.info("Checking for existing accounts.")

        active_administrators_count = get_active_admin_count(db)

        if active_administrators_count:
            logging.info(
                "Found %d active administrative accounts. Skipping initial account creation.", active_administrators_count
            )
            return

        logging.info(
            "Found no active administrative accounts. Creating an initial administrator account from the ENV configuration."
        )

        username = get_env("ADMIN_USERNAME")
        password = get_env("ADMIN_PASSWORD")

        try:
            create_user(
                db,
                CreateUserForm(
                    username=username,
                    password=password,
                    full_name="",
                    is_admin=True,
                    disabled=False,
                ),
            )
            logging.info("Admin account '%s' created successfully.", username)
        except Exception:
            logging.error("Error occurred while creating the admin account. %s")


def synchronize_database():
    """
    Removes outdated metadata entries from the database by quering the DNS provider for current data.
    """

    with session_factory() as db:
        logging.info("Synchronizing database metadata with DNS provider.")

        try:
            cleanup_zone_metadata(db)

            zone_names = db.scalars(select(DNSRecordMetadataInDB.zone_name).distinct()).all()

            cleanup_record_metadata(db, *zone_names)

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
