from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from app.database.models.action_log import ActionLogInDB
from pydantic import BaseModel, ConfigDict


class ActionLogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entry_uuid: UUID
    action_timestamp: datetime
    actor_type: Literal["user", "watcher", "automatic"]
    actor: str
    action: Literal["created", "changed", "deleted", "restored", "permanently_deleted"]
    affected_object_type: Literal["zone", "record"]
    object_before: dict[str, Any] | None = None
    object_after: dict[str, Any] | None = None

    @classmethod
    def from_db(cls, action_log_db: ActionLogInDB) -> "ActionLogEntry":
        return ActionLogEntry.model_validate(action_log_db)
