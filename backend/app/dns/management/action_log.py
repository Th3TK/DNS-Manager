from uuid import UUID

from app.database.models.action_log import ActionLogInDB
from app.dns.models.action_log import ActionLog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_log_entries(db: Session, limit: int = 100, offset=0) -> list[ActionLog]:
    action_logs_in_db = db.scalars(
        select(ActionLogInDB).order_by(ActionLogInDB.action_timestamp.desc()).offset(offset).limit(limit)
    )

    return [ActionLog.from_db(action_log_in_db) for action_log_in_db in action_logs_in_db]


def get_log_entry(db: Session, entry_uuid: UUID) -> ActionLog:
    action_log_in_db = db.scalar(select(ActionLogInDB).where(ActionLogInDB.entry_uuid == entry_uuid))

    if action_log_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action log entry with entry_uuid={entry_uuid} could not be found.",
        )

    return ActionLog.from_db(action_log_in_db)
