from typing import Annotated
from uuid import UUID

from app.database.database import get_db
from app.dns.management.action_log import get_log_entries, get_log_entry
from app.dns.models.action_log import ActionLog
from app.users.authentication import get_authenticated_user
from app.users.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/log",
    tags=["Action log"],
)


@router.get("", response_model=list[ActionLog])
def __get_list_of_action_log_entries__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 100,
    offset: int = 0,
) -> list[ActionLog]:
    return get_log_entries(db, limit, offset)


@router.get("/{entry_uuid}", response_model=ActionLog)
def __get_action_log_entry__(
    user: Annotated[User, Depends(get_authenticated_user)], db: Annotated[Session, Depends(get_db)], entry_uuid: UUID
) -> ActionLog:
    return get_log_entry(db, entry_uuid)
