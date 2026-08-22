import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.management.users.authentication import authenticate_user
from app.management.users.tokens import get_user_tokens
from app.models.tokens import Tokens
from app.providers.factory import provider

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
)


@router.get("/health", response_model=None, status_code=200, tags=["General"])
def __check_services_status__(db: Annotated[Session, Depends(get_db)]) -> None:
    # check database health, raises OperationalError which is caught by the global exception handler and HTTP 503 is raised
    db.execute(text("SELECT 1"))

    # check provider health, the method raises HTTP 503 on error
    provider.health_check()


@router.post("/login", response_model=Tokens, tags=["Authentication"])
async def __login_for_access_token__(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials.")

    return get_user_tokens(user)
