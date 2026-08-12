from typing import Optional
import uuid

from sqlalchemy import UUID, Boolean, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.database.models.enums import RecordOrigin


class DNSRecord(Base):
    __tablename__ = "dns_records"

    __table_args__ = (
        UniqueConstraint("zone", "name", "type", "content", name="unique_records_identifiers"),
    )

    # identifiers
    uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
    )
    
    zone: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    type: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    
    content: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    # metadata
    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    checks_enabled: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    
    author: Mapped[str | None] = mapped_column(ForeignKey("users.username"), nullable=False)
    
    origin: Mapped[RecordOrigin] = mapped_column(
        Enum(
            RecordOrigin, 
            name="record_origin", 
            native_enum=True
        ),
        nullable=False,
    )

    
