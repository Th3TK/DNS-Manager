from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(primary_key=True, index=True)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    disabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    
