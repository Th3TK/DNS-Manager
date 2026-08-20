import logging

from app.database.connection import session_factory
from app.management.users.users import create_user
from app.models.user import CreateUserForm
from app.utils.env import get_env

logger = logging.getLogger(__name__)


def main() -> None:
    username = get_env("ADMIN_USERNAME")
    password = get_env("ADMIN_PASSWORD")

    with session_factory() as db:
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
        except Exception as e:
            logger.error("Error occurred while creating the admin account. %s", e)


if __name__ == "__main__":
    main()
