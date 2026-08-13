import datetime as dt
import logging
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError, decode, encode
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import ENV_CONFIG
from app.database.database import get_db
from app.users.models.user import User
from app.users.users import get_user, get_user_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)


Token = Annotated[str, Depends(oauth2_scheme)]

DatabaseSession = Annotated[Session, Depends(get_db)]

class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    
TokenTypes = Literal['access', 'refresh']
    
class DecodedTokenPayload(BaseModel):
    subject: str
    expiration_date: dt.datetime
    token_type: TokenTypes



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password) -> str:
    return pwd_context.hash(plain_password)


def create_token(token_type: TokenTypes, user: User, expires_delta: dt.timedelta) -> str:
    to_encode = {
        "token_type": token_type,
        "sub": str(user.username),
        "exp": dt.datetime.now(dt.timezone.utc) + expires_delta
    }
    return encode(to_encode, ENV_CONFIG.AUTHENTICATION_SECRET_KEY, algorithm="HS256")


def create_access_token(user: User) -> str:
    return create_token("access", user, dt.timedelta(seconds=ENV_CONFIG.ACCESS_TOKEN_LIFETIME_SECONDS))


def create_refresh_token(user: User) -> str:
    return create_token("refresh", user, dt.timedelta(seconds=ENV_CONFIG.REFRESH_TOKEN_LIFETIME_SECONDS))


def get_user_tokens(user: User):
    return Tokens(
        access_token = create_access_token(user),
        refresh_token = create_refresh_token(user),
    )
    

def is_token_of_type(payload: DecodedTokenPayload, token_type: TokenTypes):
    return payload.token_type == token_type


def is_access_token(payload: DecodedTokenPayload):
    return is_token_of_type(payload, 'access')


def is_refresh_token(payload: DecodedTokenPayload):
    return is_token_of_type(payload, 'refresh')


def decode_token(token: str) -> DecodedTokenPayload:
    payload = decode(token, ENV_CONFIG.AUTHENTICATION_SECRET_KEY, algorithms=["HS256"])
    
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



def authenticate_user(db: Session, username: str, password: str) -> User | Literal[False]:
    user = get_user(db, username)
    
    if not user or user.disabled:
        return False
    
    password_in_db = get_user_password(db, username)
    
    if not verify_password(password, password_in_db):
        return False
    
    return user


def get_authenticated_user(db: DatabaseSession, token: Token) -> User: 
    return validate_user_token(db, token, 'access')


def get_authenticated_administrator(db: DatabaseSession, token: Token) -> User:
    user = validate_user_token(db, token, 'access')
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="You do not have the necessary permissions to access this resource.")    
    return user


def get_user_from_refresh_token(db: DatabaseSession, token: Token) -> User:
    return validate_user_token(db, token, 'refresh')