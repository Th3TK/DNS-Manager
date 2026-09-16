import logging

from alembic import command
from alembic.config import Config
from sqlalchemy.exc import OperationalError

from app.database.connection import session_factory
from app.management.users.users import create_user, get_active_admin_count
from app.models.user import CreateUserForm
from app.utils.env import get_env

logger = logging.getLogger(__name__)


def run_migrations():
    logger.info("Starting database migrations.")

    try:
        command.upgrade(Config("alembic.ini"), "head")
        logger.info("Database migrations completed.")
    except OperationalError:
        logging.critical(
            "Database migrations FAILED. Could not connect to the database. Ensure that the PostgreSQL database is running "
            "and that the database connection settings in the environment variables are correctly configured."
        )
        logger.critical("Critical error occured during startup - EXITING")
        raise SystemExit(1)
    except Exception as exc:
        logging.critical("Database migrations FAILED. %s", str(exc))
        logger.critical("Critical error occured during startup - EXITING")
        raise SystemExit(1)


def create_first_account():
    """
    Creates initial user if there are no active administrators in the users table is empty.
    """

    with session_factory() as db:
        try:
            logger.info("Checking for existing accounts.")

            active_administrators_count = get_active_admin_count(db)

            if active_administrators_count:
                logger.info(
                    "Found %d active administrative accounts. Skipping initial account creation.", active_administrators_count
                )
                return

            logger.info(
                "Found no active administrative accounts. Creating an initial administrator account from the ENV configuration."
            )
        except Exception:
            logging.critical(
                "Error occured during retrieving application accounts. Ensure that the PostgreSQL database is running and that "
                "the database connection settings in the environment variables are correctly configured."
            )
            logger.critical("Critical error occured during startup - EXITING")
            raise SystemExit(1)

        username = get_env("ADMIN_USERNAME")
        password = get_env("ADMIN_PASSWORD")

        try:
            create_user(
                db,
                CreateUserForm(
                    username=username,
                    password=password,
                    full_name="",
                    is_admin=True,
                    disabled=False,
                ),
            )
            logger.info("Admin account '%s' created successfully.", username)
        except Exception as exc:
            logger.critical(f"Error occured during creating the initial account: {exc}")
            logger.critical("Critical error occured during startup - EXITING")
            raise SystemExit(1)
