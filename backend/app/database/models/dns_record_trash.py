import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.database.models.enums import ActorType


class DNSRecordTrash(Base):
    __tablename__ = "dns_record_trash"

    uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dns_records.uuid", ondelete="CASCADE", name="fk_dns_record_trash_uuid_dns_records",),
        primary_key=True,
    )

    deletion_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    actor_type: Mapped[ActorType] = mapped_column(
        Enum(
            ActorType, 
            native_enum=True,
            name="dns_record_trash_actor_type", 
        ), 
        nullable=False)

    actor: Mapped[str] = mapped_column(String, nullable=False)