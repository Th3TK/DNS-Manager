import logging

import requests
from app.config import ENV_CONFIG
from app.database.connection import session_factory
from app.dns.factory import provider
from app.dns.management.record import cleanup_record_metadata
from app.dns.management.zone import cleanup_zone_metadata
from app.dns.validators.base import DNSValidationError
from app.endpoints.action_log import router as action_log_router
from app.endpoints.authentication import router as authentication_router
from app.endpoints.base import router as base_router
from app.endpoints.dns_management import router as dns_management_router
from app.endpoints.trash import router as dns_trash_router
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=getattr(logging, ENV_CONFIG.LOG_LEVEL))

logger = logging.getLogger(__name__)


# Synchronize the database with the DNS provider
with session_factory() as db:
    logging.info("Synchronizing database metadata with DNS provider.")

    try:
        removed_zones: int = cleanup_zone_metadata(db)
        logging.info("Removed %d stale zones from the database.", removed_zones)

        zones = provider.get_zones()
        zone_ids = {zone.id for zone in zones}

        removed_records: int = cleanup_record_metadata(db, *zone_ids)
        logging.info("Removed %d stale records from the database.", removed_records)
        logging.info("Database synchronization with DNS provider completed.")
    except Exception as exc:
        logging.error("Database synchronization with DNS provider FAILED.")
        if ENV_CONFIG.DNS_PROVIDER == "powerdns" and isinstance(exc, HTTPException):
            if exc.status_code == status.HTTP_401_UNAUTHORIZED:
                logging.error(
                    "Database synchronization failed because PowerDNS rejected the request as unauthorized. "
                    "Ensure the POWERDNS_API_KEY environment variable is set correctly."
                )
            elif exc.status_code == status.HTTP_404_NOT_FOUND:
                logging.error(
                    "Database synchronization failed because the PowerDNS API resource path was invalid. "
                    "Ensure the POWERDNS_API_URL and POWERDNS_SERVER_ID environment variables are set correctly."
                )


# Initiate the FastAPI instance
app = FastAPI(root_path="/api")


@app.exception_handler(OperationalError)
async def sqlalchemy_connection_error_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": (
                "Could not connect to the database. Ensure that the PostgreSQL "
                "database is running and that the database connection settings "
                "in the environment variables are correctly configured."
            )
        },
    )


@app.exception_handler(requests.exceptions.JSONDecodeError)
async def internal_request_json_parsing_error(request: Request, exc: requests.exceptions.JSONDecodeError):
    logging.critical("Unhandled exception: The response from an external API could not be parsed as JSON.", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "The response from an external API could not be parsed as JSON."},
    )


@app.exception_handler(DNSValidationError)
async def dns_validation_error(request: Request, exc: DNSValidationError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


app.include_router(base_router)
app.include_router(authentication_router)
app.include_router(dns_management_router)
app.include_router(dns_trash_router)
app.include_router(action_log_router)
