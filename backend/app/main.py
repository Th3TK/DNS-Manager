import logging
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from sqlalchemy.exc import OperationalError

from app.config import ENV_CONFIG
from app.endpoints.action_log import router as action_log_router
from app.endpoints.authentication import router as authentication_router
from app.endpoints.dns import router as dns_router
from app.endpoints.health import router as base_router
from app.endpoints.name_search import router as name_search_router
from app.endpoints.status_check import router as status_check_router
from app.endpoints.trash import router as trash_router
from app.endpoints.user import router as users_router
from app.management.status_check.status_check import automatic_status_check
from app.management.trash.cleanup import automatic_trash_removal
from app.models.exceptions import DependencyExceptionCodes, DNSProviderException, DNSValidationError
from app.synch import synchronize_database

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

    await automatic_status_check.start()
    logging.info("Scheduled automatic record status check.")

    yield

    automatic_trash_removal.stop()
    await automatic_status_check.stop()


# Initiate the FastAPI instance
app = FastAPI(root_path="/api", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow local origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(OperationalError)
async def sqlalchemy_connection_error_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": (
                "Could not connect to the database. Ensure that the PostgreSQL "
                "database is running and that the database connection settings "
                "in the environment variables are correctly configured."
            ),
            "code": DependencyExceptionCodes.DATABASE,
        },
    )


@app.exception_handler(DNSProviderException)
async def dns_provider_error_handler(request: Request, exc: DNSProviderException):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": str(exc),
            "code": DependencyExceptionCodes.DNS_PROVIDER,
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
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


app.include_router(base_router)
app.include_router(authentication_router)
app.include_router(dns_router)
app.include_router(name_search_router)
app.include_router(trash_router)
app.include_router(action_log_router)
app.include_router(users_router)
app.include_router(status_check_router)


# Add an OAuth2 security scheme to the OpenAPI schema so Swagger UI
# always displays the Authorize button, despite authentication using
# HTTP-only cookies.
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                }
            },
        }
    }

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi

add_pagination(app)
