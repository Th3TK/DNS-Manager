import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.database.models.enums import DNSObjectType


class DNSTrashInDB(Base):
    __tablename__ = "dns_trash"

    entry_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    deletion_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    actor: Mapped[str] = mapped_column(index=True, nullable=False)

    object_type: Mapped[DNSObjectType] = mapped_column(
        Enum(DNSObjectType, native_enum=True, name="dns_trash_object_type"), nullable=False, index=True
    )

    object_data: Mapped[dict[str, Any]] = mapped_column(JSONB)
