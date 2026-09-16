import logging
import threading

from src.config import ENV_CONFIG
from src.managers.messenger import APIMessenger
from src.managers.watcher import DockerWatcher

logger = logging.getLogger(__name__)


def validate_env():
    # Ensure consistency with usernames. Usernames cannot be longer than 64 characters.
    # Watcher actions will are saved in the database under actor "watcher:<WATCHER_NAME>".
    # 56 characters are the limit for that string not to exceed 64 characters.
    if len(ENV_CONFIG.WATCHER_NAME) > 56:
        raise ValueError("WATCHER_NAME cannot be longer than 56 characters")


def main():
    logging.basicConfig(
        level=getattr(logging, ENV_CONFIG.LOG_LEVEL),
        format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    validate_env()

    try:
        logger.info("Initializing Docker events watcher.")

        api_messenger = APIMessenger()
        docker_watcher = DockerWatcher(messenger=api_messenger)

        docker_watcher.start()
        docker_watcher.start_sync()

        logger.info("Successfully initialized Docker events watcher.")

    except Exception:
        logger.exception("Error occurred during watcher initialization.")

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        logger.info("Stopping Docker events watcher.")


if __name__ == "__main__":
    main()
