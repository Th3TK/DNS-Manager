import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import ENV_CONFIG
from app.database.database import get_db
from app.management.users.authentication import authenticate_user, get_user_from_refresh_token
from app.management.users.tokens import get_user_tokens
from app.models.tokens import Tokens
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    path="/token",
    response_model=Tokens,
    summary="Authenticate user",
    description="If credentials are valid, returns an access token and a refresh token.",
)
async def __retrieve_tokens__(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials.")

    return get_user_tokens(user)


@router.post(
    path="/login",
    response_model=None,
    summary="Authenticate user (HTTP cookie)",
    description="If the credentials are valid, sets HttpOnly authentication cookies.",
)
async def __login__(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    response: Response,
):
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
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=ENV_CONFIG.HTTPS_ENABLED,
        samesite="lax",
    )


@router.post(path="/refresh", response_model=None, summary="Refresh tokens (HTTP cookie)")
async def __refresh_tokens__(
    user: Annotated[User, Depends(get_user_from_refresh_token)],
    db: Annotated[Session, Depends(get_db)],
    response: Response,
):
    tokens = get_user_tokens(user)

    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=ENV_CONFIG.HTTPS_ENABLED,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=ENV_CONFIG.HTTPS_ENABLED,
        samesite="lax",
    )
