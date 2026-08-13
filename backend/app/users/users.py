from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.user import UserInDB
from app.users.models.user import User


def get_raw_user(db: Session, username: str) -> UserInDB | None:
    return db.scalar(select(UserInDB).where(UserInDB.username == username))

def get_user_password(db: Session, username: str) -> str | None:
    return db.scalar(select(UserInDB.password).where(UserInDB.username == username))

def get_user(db: Session, username: str) -> User | None:
    raw_user = get_raw_user(db, username)
    
    if raw_user is not None:
        return User(
            username=raw_user.username,
            full_name=raw_user.full_name,
            is_admin=raw_user.is_admin,
            disabled=raw_user.disabled
        )
    
    