import uuid
from datetime import datetime
from typing import Any

from app.database.database import Base
from app.database.models.enums import ActionObjectType, ActorType, ChangeAction
from sqlalchemy import DateTime, Enum, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column


class ActionLogInDB(Base):
    __tablename__ = "action_log"

    entry_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    action_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    actor_type: Mapped[ActorType] = mapped_column(Enum(ActorType, native_enum=True), nullable=False)

    actor: Mapped[str] = mapped_column(index=True, nullable=False)

    action: Mapped[ChangeAction] = mapped_column(Enum(ChangeAction, native_enum=True), index=True, nullable=False)

    affected_object_type: Mapped[ActionObjectType] = mapped_column(
        Enum(ActionObjectType, native_enum=True), nullable=False, index=True
    )

    object_before: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    object_after: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
