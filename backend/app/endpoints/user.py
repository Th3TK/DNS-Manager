from typing import Annotated

from app.database.database import get_db
from app.management.users.authentication import get_authenticated_administrator, get_authenticated_user
from app.management.users.users import change_password, create_user, delete_user, get_user, get_users, modify_user
from app.models.user import ChangePasswordForm, CreateUserForm, ModifyUserForm, User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=User)
def __get_me__(
    user: Annotated[User, Depends(get_authenticated_user)],
):
    return user


@router.patch("/me/change-password", response_model=None, status_code=204)
def __change_own_password__(
    user: Annotated[User, Depends(get_authenticated_user)], db: Annotated[Session, Depends(get_db)], form: ChangePasswordForm
) -> None:
    return change_password(db, user, form.password)


@router.get("", response_model=list[User])
def __get_users__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
) -> list[User]:
    return get_users(db)


@router.get("/{username}", response_model=User)
def __get_user__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    username: str,
) -> User:
    response = get_user(db, username)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username='{username}' could not be found.",
        )

    return response


@router.post("", response_model=User)
def __create_user__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    form: CreateUserForm,
) -> User:
    return create_user(db, form)


@router.patch("/{username}", response_model=User)
def __modify_user__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    form: ModifyUserForm,
    username: str,
) -> User:
    return modify_user(db, username, form)


@router.delete("/{username}", response_model=None, status_code=204)
def __delete_user__(
    user: Annotated[User, Depends(get_authenticated_administrator)],
    db: Annotated[Session, Depends(get_db)],
    username: str,
) -> None:
    return delete_user(db, username)
