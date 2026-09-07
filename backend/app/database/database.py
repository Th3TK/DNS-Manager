from collections.abc import Generator

from sqlalchemy.orm import DeclarativeBase, Session

from app.database.connection import session_factory


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    with session_factory() as session:
        yield session
