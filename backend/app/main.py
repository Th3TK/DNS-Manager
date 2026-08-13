import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.config import ENV_CONFIG
from app.endpoints.authentication import router as authentication_router
from app.endpoints.dns_management import router as dns_management_router

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

app.include_router(authentication_router)
app.include_router(dns_management_router)