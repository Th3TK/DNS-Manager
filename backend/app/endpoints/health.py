import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from psycopg import connect

from app.config import ENV_CONFIG
from app.models.exceptions import DependencyExceptionCodes, DNSProviderException
from app.providers.factory import provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Health"])


@router.get("/health", status_code=200)
def __check_services_status__():
    errors = []

    try:
        with connect(ENV_CONFIG.DATABASE_URL, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
    except Exception:
        errors.append(
            {
                "detail": "Could not connect to the database. Ensure that the PostgreSQL "
                "database is running and that the database connection settings "
                "in the environment variables are correctly configured.",
                "code": DependencyExceptionCodes.DATABASE,
            }
        )

    try:
        provider.health_check()
    except DNSProviderException as exc:
        errors.append(
            {
                "detail": str(exc),
                "code": DependencyExceptionCodes.DNS_PROVIDER,
            }
        )
    except Exception:
        logging.exception(
            "Unhandled exception occured during provider health check."
            "Provider should raise DNSProviderException on all known exceptions."
        )
        errors.append(
            {
                "detail": "Could not connect to the DNS provider.",
                "code": DependencyExceptionCodes.DNS_PROVIDER,
            }
        )

    if errors:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=errors,
        )
