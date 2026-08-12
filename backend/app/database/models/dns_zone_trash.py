import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.database.models.enums import ActorType


class DNSZoneTrash(Base):
    __tablename__ = "dns_zone_trash"

    uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dns_zones.uuid", ondelete="CASCADE", name="fk_dns_zone_trash_uuid_dns_records",),
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
            name="dns_zone_trash_actor_type", 
            native_enum=True
        ), 
        nullable=False)

    actor: Mapped[str] = mapped_column(String, nullable=False)