import logging
from typing import Annotated

from app.database.database import get_db
from app.dns.factory import provider
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["General"],
)


@router.get("/health", response_model=None, status_code=200)
def __check_services_status__(db: Annotated[Session, Depends(get_db)]) -> None:
    # check database health, raises OperationalError which is caught by the global exception handler and HTTP 503 is raised
    db.execute(text("SELECT 1"))

    # check provider health, the method raises HTTP 503 on error
    provider.health_check()
