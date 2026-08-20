from app.config import ENV_CONFIG
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_sqlalchemy_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


engine = create_engine(get_sqlalchemy_database_url(ENV_CONFIG.DATABASE_URL))

session_factory = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
