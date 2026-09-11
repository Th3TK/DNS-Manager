from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.management.action_log.action_log import get_all_actors, get_log_entries_query, get_log_entry
from app.management.users.authentication import get_authenticated_user
from app.models.action_log import ActionLogEntry
from app.models.user import User

router = APIRouter(
    prefix="/change-history",
    tags=["Change history"],
)


@router.get("", response_model=Page[ActionLogEntry])
def __get_list_of_action_log_entries__(
    user: Annotated[User, Depends(get_authenticated_user)],
    db: Annotated[Session, Depends(get_db)],
    action: Literal["created", "changed", "deleted", "restored", "permanently_deleted"] | None = Query(None),
    actor: str | None = Query(None),
    affected_object_type: Literal["record", "zone"] | None = Query(None),
    affected_object_name: str | None = Query(None),
    action_timestamp_min: int | None = Query(None),
    action_timestamp_max: int | None = Query(None),
):
    query = get_log_entries_query(
        action=action,
        actor=actor,
        affected_object_name=affected_object_name,
        affected_object_type=affected_object_type,
        action_timestamp_min=action_timestamp_min,
        action_timestamp_max=action_timestamp_max,
    )

    return paginate(db, query)


@router.get("/actors", response_model=list[str])
def __get_all_actors_from_change_history__(
    user: Annotated[User, Depends(get_authenticated_user)], db: Annotated[Session, Depends(get_db)]
) -> list[str]:
    return get_all_actors(db)


@router.get("/{entry_uuid}", response_model=ActionLogEntry)
def __get_action_log_entry__(
    user: Annotated[User, Depends(get_authenticated_user)], db: Annotated[Session, Depends(get_db)], entry_uuid: UUID
) -> ActionLogEntry:
    return get_log_entry(db, entry_uuid)
