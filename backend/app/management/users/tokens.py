from datetime import datetime, timedelta, timezone

from app.config import ENV_CONFIG
from app.management.users.users import get_user
from app.models.tokens import DecodedTokenPayload, Tokens, TokenTypes
from app.models.user import User
from fastapi import HTTPException, Request, status
from jwt import ExpiredSignatureError, InvalidTokenError, decode, encode
from sqlalchemy.orm import Session


def create_token(token_type: TokenTypes, user: User, expires_delta: timedelta) -> str:
    to_encode = {"token_type": token_type, "sub": str(user.username), "exp": datetime.now(timezone.utc) + expires_delta}
    return encode(to_encode, ENV_CONFIG.AUTH_SECRET_KEY, algorithm="HS256")


def create_access_token(user: User) -> str:
    return create_token("access", user, timedelta(seconds=ENV_CONFIG.ACCESS_TOKEN_LIFETIME_SECONDS))


def create_refresh_token(user: User) -> str:
    return create_token("refresh", user, timedelta(seconds=ENV_CONFIG.REFRESH_TOKEN_LIFETIME_SECONDS))


def get_user_tokens(user: User):
    return Tokens(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


def is_token_of_type(payload: DecodedTokenPayload, token_type: TokenTypes):
    return payload.token_type == token_type


def is_access_token(payload: DecodedTokenPayload):
    return is_token_of_type(payload, "access")


def is_refresh_token(payload: DecodedTokenPayload):
    return is_token_of_type(payload, "refresh")


def decode_token(token: str) -> DecodedTokenPayload:
    payload = decode(token, ENV_CONFIG.AUTH_SECRET_KEY, algorithms=["HS256"])

    subject = payload.get("sub")
    expiration_date = payload.get("exp")
    token_type = payload.get("token_type")

    if not subject or not expiration_date or not token_type:
        raise InvalidTokenError()

    return DecodedTokenPayload(
        subject=subject,
        expiration_date=expiration_date,
        token_type=token_type,
    )


def validate_user_token(db: Session, token: str, token_type: TokenTypes) -> User:
    try:
        payload = decode_token(token)

        if not is_token_of_type(payload, token_type):
            raise InvalidTokenError()

        username = payload.subject
        user = get_user(db, username)

        if user is None or user.disabled:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")

        return user

    except (InvalidTokenError, ExpiredSignatureError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")


def get_tokens(
    request: Request,
) -> Tokens:
    return Tokens(
        access_token=request.cookies.get("access_token") or "",
        refresh_token=request.cookies.get("refresh_token") or "",
    )
