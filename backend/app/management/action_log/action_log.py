import logging
from itertools import zip_longest
from typing import Any
from uuid import UUID

from app.database.models.action_log import ActionLogInDB
from app.database.models.enums import ActorType, ChangeAction, DNSObjectType
from app.models.action_log import ActionLogEntry
from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_log_entries_query(
    db: Session, action: ChangeAction | None = None, actor: str | None = None, affected_object_name: str | None = None
) -> Select:
    query = select(ActionLogInDB).order_by(ActionLogInDB.action_timestamp.desc())

    if action is not None:
        query = query.where(ActionLogInDB.action == action)

    if actor is not None:
        query = query.where(ActionLogInDB.actor == actor)

    if affected_object_name is not None:
        query = query.where(ActionLogInDB.affected_object_name.contains(affected_object_name))

    return query


def get_log_entry(db: Session, entry_uuid: UUID) -> ActionLogEntry:
    action_log_in_db = db.scalar(select(ActionLogInDB).where(ActionLogInDB.entry_uuid == entry_uuid))

    if action_log_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action log entry with entry_uuid='{entry_uuid}' could not be found.",
        )

    return ActionLogEntry.from_db(action_log_in_db)


def create_log_entry(
    db: Session,
    actor_type: ActorType,
    actor: str,
    action: ChangeAction,
    affected_object_type: DNSObjectType,
    affected_object_name: str,
    object_before: dict[str, Any] | None,
    object_after: dict[str, Any] | None,
) -> None:
    log = ActionLogInDB(
        actor_type=actor_type,
        actor=actor,
        action=action,
        affected_object_type=affected_object_type,
        affected_object_name=affected_object_name,
        object_before=object_before,
        object_after=object_after,
    )

    try:
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

        logger.exception(
            "Failed to save action log in the database:\n  Action: %s\n  Object type: %s\n  Actor: %s\n  Before: %s\n  After: %s",
            action.upper(),
            affected_object_type.upper(),
            actor,
            object_before,
            object_after,
        )


def create_log_entries(
    db: Session,
    actor_type: ActorType,
    actor: str,
    action: ChangeAction,
    affected_object_type: DNSObjectType,
    objects_before: list[dict[str, Any]] | None,
    objects_after: list[dict[str, Any]] | None,
) -> None:

    logs = [
        ActionLogInDB(
            actor_type=actor_type,
            actor=actor,
            action=action,
            affected_object_type=affected_object_type,
            object_before=object_before,
            object_after=object_after,
        )
        for object_before, object_after in zip_longest(
            objects_before or [],
            objects_after or [],
            fillvalue=None,
        )
    ]

    try:
        db.add_all(logs)
        db.commit()
    except Exception:
        db.rollback()

        logger.exception(
            "Failed to save action logs in the database:"
            "\n  Action: %s\n  Object type: %s\n  Actor: %s\n  Before: %s\n  After: %s",
            action.upper(),
            affected_object_type.upper(),
            actor,
            objects_before,
            objects_after,
        )


def get_all_actors(db: Session) -> list[str]:
    return [actor for (actor,) in db.query(ActionLogInDB.actor).distinct().all()]
