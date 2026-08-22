import argparse
import logging

from app.database.connection import session_factory
from app.management.users.users import create_user, get_active_admin_count
from app.models.user import CreateUserForm
from app.utils.env import get_env


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="Create the admin account even if an active admin already exists.",
    )
    args = parser.parse_args()

    username = get_env("ADMIN_USERNAME")
    password = get_env("ADMIN_PASSWORD")

    with session_factory() as db:
        admins_count = get_active_admin_count(db)

        if admins_count and not args.force:
            logging.warning(
                "An active admin account already exists. No admin account was created. Use --force to create one anyway."
            )
            raise SystemExit(0)

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
            logging.info("Admin account '%s' created successfully.", username)

        except Exception as exc:
            logging.error("Error occurred while creating the admin account. %s", exc)
            raise SystemExit(1)


if __name__ == "__main__":
    main()
