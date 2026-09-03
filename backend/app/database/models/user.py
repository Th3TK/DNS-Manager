from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class UserInDB(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False, default="", server_default="")
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False, server_default="false")
    disabled: Mapped[bool] = mapped_column(default=False, nullable=False, server_default="false")
