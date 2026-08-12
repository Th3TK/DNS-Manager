import uuid

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class DNSZone(Base):
    __tablename__ = "dns_zones"

    # identifiers
    uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # metadata
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    
    author: Mapped[str | None] = mapped_column(ForeignKey("users.username"), nullable=True)

    
