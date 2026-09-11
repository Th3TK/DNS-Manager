import logging

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def run_migrations():
    logger.info("Starting database migrations.")

    try:
        command.upgrade(Config("alembic.ini"), "head")
        logger.info("Database migrations completed.")
    except Exception:
        logging.error("Database migrations FAILED.")
