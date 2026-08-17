import logging

import requests
from app.config import ENV_CONFIG
from app.endpoints.action_log import router as action_log_router
from app.endpoints.authentication import router as authentication_router
from app.endpoints.dns_management import router as dns_management_router
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=getattr(logging, ENV_CONFIG.LOG_LEVEL))

logger = logging.getLogger(__name__)


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


app.include_router(authentication_router)
app.include_router(dns_management_router)
app.include_router(action_log_router)
