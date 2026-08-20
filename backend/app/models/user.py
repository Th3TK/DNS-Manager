from typing import Annotated

from app.database.models.user import UserInDB
from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    full_name: str = ""
    is_admin: bool
    disabled: bool

    @classmethod
    def from_db(cls, user_db: UserInDB) -> "User":
        return User.model_validate(user_db)


class CreateUserForm(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    password: Annotated[str, Field(min_length=6, max_length=128)]
    full_name: Annotated[str, Field(max_length=128, default="")]
    is_admin: bool = False
    disabled: bool = False


class ModifyUserForm(BaseModel):
    password: Annotated[str, Field(min_length=6, max_length=128)] | None = None
    full_name: Annotated[str, Field(max_length=128, default="")] | None = None
    is_admin: bool | None = None
    disabled: bool | None = None


class ChangePasswordForm(BaseModel):
    password: Annotated[str, Field(min_length=6, max_length=128)]
