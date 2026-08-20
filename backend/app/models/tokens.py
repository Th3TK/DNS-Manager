from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


TokenTypes = Literal["access", "refresh"]


class DecodedTokenPayload(BaseModel):
    subject: str
    expiration_date: datetime
    token_type: TokenTypes
