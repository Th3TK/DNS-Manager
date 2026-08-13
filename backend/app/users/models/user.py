from pydantic import BaseModel


class User(BaseModel):
    username: str
    full_name: str = ""
    is_admin: bool
    disabled: bool