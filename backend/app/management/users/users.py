import logging

from app.database.models.user import UserInDB
from app.management.users.passwords import hash_password
from app.management.users.validation import validate_username
from app.models.user import CreateUserForm, ModifyUserForm, User
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_raw_user(db: Session, username: str) -> UserInDB | None:
    return db.scalar(select(UserInDB).where(UserInDB.username == username))


def get_user_password(db: Session, username: str) -> str | None:
    return db.scalar(select(UserInDB.password).where(UserInDB.username == username))


def get_user(db: Session, username: str) -> User | None:
    raw_user = get_raw_user(db, username)

    if raw_user is None:
        return None

    return User.from_db(raw_user)


def get_users(db: Session) -> list[User]:
    users = db.scalars(select(UserInDB))

    return [User.from_db(user) for user in users]


def create_user(db: Session, creation_form: CreateUserForm) -> User:
    duplicate = get_user(db, creation_form.username)

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username='{creation_form.username}' already exists.",
        )

    validate_username(creation_form.username)

    user_in_db = UserInDB(
        **creation_form.model_dump(exclude={"password"}),
        password=hash_password(creation_form.password),
    )

    try:
        db.add(user_in_db)
        db.commit()
    except Exception:
        logger.exception("Internal error occured during user creation.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error occured during user creation.",
        )

    return User.from_db(user_in_db)


def modify_user(db: Session, username: str, modification_form: ModifyUserForm) -> User:
    user_in_db = get_raw_user(db, username)

    if user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username='{username}' could not be found.",
        )

    updates = modification_form.model_dump(exclude_none=True)

    for field, value in updates.items():
        setattr(user_in_db, field, value)

    if updates:
        db.commit()

    return User.from_db(user_in_db)


def delete_user(db: Session, username: str) -> None:
    user_in_db = get_raw_user(db, username)

    if user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username='{username}' could not be found.",
        )

    db.delete(user_in_db)
    db.commit()


def change_password(db: Session, logged_in_user: User, new_password: str) -> None:
    db.execute(update(UserInDB).where(UserInDB.username == logged_in_user.username).values(password=hash_password(new_password)))
    db.commit()
