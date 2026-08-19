from typing import Optional

from app.database.database import Base
from app.database.models.enums import InternalRecordOrigin
from sqlalchemy import Boolean, Enum, ForeignKey, ForeignKeyConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column


class DNSRecordMetadataInDB(Base):
    __tablename__ = "dns_records_metadata"

    __table_args__ = (
        Index("ix_dns_records_metadata_zone_name", "zone_id"),
        ForeignKeyConstraint(
            ["zone_id"],
            ["dns_zones_metadata.id"],
            name="fk_dns_records_metadata_zone_id",
            ondelete="CASCADE",
        ),
    )

    # identified by the zone name along with the record type, name and content.
    zone_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    name: Mapped[str] = mapped_column(String(255), primary_key=True)

    type: Mapped[str] = mapped_column(String(10), primary_key=True)

    # metadata
    comment: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    checks_enabled: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    author: Mapped[str | None] = mapped_column(ForeignKey("users.username"), nullable=True)

    origin: Mapped[InternalRecordOrigin] = mapped_column(
        Enum(InternalRecordOrigin, name="internal_record_origin", native_enum=True),
        nullable=False,
    )
