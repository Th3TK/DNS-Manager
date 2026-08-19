import logging
from typing import Any
from uuid import UUID

from app.database.models.action_log import ActionLogInDB
from app.database.models.enums import ActorType, ChangeAction, DNSObjectType
from app.dns.models.action_log import ActionLogEntry
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_log_entries(db: Session, limit: int = 100, offset=0) -> list[ActionLogEntry]:
    action_logs_in_db = db.scalars(
        select(ActionLogInDB).order_by(ActionLogInDB.action_timestamp.desc()).offset(offset).limit(limit)
    )

    return [ActionLogEntry.from_db(action_log_in_db) for action_log_in_db in action_logs_in_db]


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
    object_before: dict[str, Any] | None,
    object_after: dict[str, Any] | None,
) -> None:
    log = ActionLogInDB(
        actor_type=actor_type,
        actor=actor,
        action=action,
        affected_object_type=affected_object_type,
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
