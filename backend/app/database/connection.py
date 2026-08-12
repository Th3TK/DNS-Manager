from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import ENV_CONFIG

engine = create_async_engine(ENV_CONFIG.DATABASE_URL)

session_factory = async_sessionmaker(engine, expire_on_commit=False)