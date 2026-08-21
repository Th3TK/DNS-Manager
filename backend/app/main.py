import logging
from contextlib import asynccontextmanager

import requests
from app.config import ENV_CONFIG
from app.endpoints.action_log import router as action_log_router
from app.endpoints.base import router as base_router
from app.endpoints.dns import router as dns_router
from app.endpoints.trash import router as trash_router
from app.endpoints.user import router as users_router
from app.management.dns.validation import DNSValidationError
from app.management.trash.cleanup import automatic_trash_removal
from app.synch import synchronize_database
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

logging.basicConfig(
    level=getattr(logging, ENV_CONFIG.LOG_LEVEL),
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.getLogger("passlib").disabled = True

logger = logging.getLogger(__name__)


# Synchronize the database with the DNS provider
synchronize_database()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await automatic_trash_removal.initialize()
    logging.info("Initialized trash removal event loop.")
    automatic_trash_removal.start()
    logging.info("Scheduled automatic trash removal.")

    yield

    automatic_trash_removal.stop()


# Initiate the FastAPI instance
app = FastAPI(root_path="/api", lifespan=lifespan)


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
app.include_router(users_router)
app.include_router(dns_router)
app.include_router(trash_router)
app.include_router(action_log_router)
