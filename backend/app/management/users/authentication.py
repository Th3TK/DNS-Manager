import logging
from typing import Annotated, Literal

from app.database.database import get_db
from app.management.users.passwords import verify_password
from app.management.users.tokens import get_tokens, validate_user_token
from app.management.users.users import get_user, get_user_password
from app.models.tokens import Tokens
from app.models.user import User
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

DatabaseSession = Annotated[Session, Depends(get_db)]


def authenticate_user(db: Session, username: str, password: str) -> User | Literal[False]:
    user = get_user(db, username)

    if not user or user.disabled:
        return False

    password_in_db = get_user_password(db, username)

    if not verify_password(password, password_in_db):
        return False

    return user


def get_authenticated_user_from_token(db: Session, access_token: str) -> User:
    return validate_user_token(db, access_token, "access")


def get_authenticated_user(db: DatabaseSession, tokens: Annotated[Tokens, Depends(get_tokens)]) -> User:
    return validate_user_token(db, tokens.access_token, "access")


def get_authenticated_administrator(db: DatabaseSession, tokens: Annotated[Tokens, Depends(get_tokens)]) -> User:
    user = validate_user_token(db, tokens.access_token, "access")

    if not user.is_admin:
        raise HTTPException(status_code=403, detail="You do not have the necessary permissions to access this resource.")

    return user


def get_user_from_refresh_token(db: DatabaseSession, tokens: Annotated[Tokens, Depends(get_tokens)]) -> User:
    return validate_user_token(db, tokens.refresh_token, "refresh")
