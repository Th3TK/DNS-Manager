
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class DNSZoneMetadataInDB(Base):
    __tablename__ = "dns_zones_metadata"

    # identified by the name
    name: Mapped[str] = mapped_column(String(255), nullable=False, primary_key=True)
    
    # metadata
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    
    author: Mapped[str | None] = mapped_column(ForeignKey("users.username"), nullable=True)

    
