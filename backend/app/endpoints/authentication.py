import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import ENV_CONFIG
from app.database.database import get_db
from app.management.users.authentication import authenticate_user, get_user_from_refresh_token
from app.management.users.tokens import get_user_tokens
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    path="/login",
    response_model=Literal[True],
    summary="Authenticate user (HTTP cookie)",
    description="If the credentials are valid, sets HttpOnly authentication cookies.",
)
async def __login__(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> Literal[True]:
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials.")

    tokens = get_user_tokens(user)

    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=ENV_CONFIG.HTTPS_ENABLED,
        samesite="lax",
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=ENV_CONFIG.HTTPS_ENABLED,
        samesite="lax",
        path="/auth/refresh",
    )

    return True


@router.post(path="/refresh", response_model=Literal[True], summary="Refresh tokens (HTTP cookie)")
async def __refresh_tokens__(
    user: Annotated[User, Depends(get_user_from_refresh_token)],
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> Literal[True]:
    tokens = get_user_tokens(user)

    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=ENV_CONFIG.HTTPS_ENABLED,
        samesite="lax",
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=ENV_CONFIG.HTTPS_ENABLED,
        samesite="lax",
        path="/auth/refresh",
    )

    return True
