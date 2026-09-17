import logging
import threading
from datetime import datetime, timedelta, timezone

from app.database.connection import session_factory
from app.database.models.dns_trash import DNSTrashInDB
from app.database.models.enums import ActorType, ChangeAction
from app.management.action_log.action_log import create_log_entry
from app.models.trash import TrashEntry
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

logger = logging.getLogger(__name__)

ITEM_TRASH_TIME_TO_LIVE_SECONDS = 2592000  # 30 days


class AutomaticTrashRemoval:
    """
    Schedules automatic trash removals.

    On start, it retrieves the oldest trash entry from the database and sets a future task to remove it.
    Once the entry's time to live expires, permanently removes it from the trash table.
    After doing so, it retrieves the next oldest trash entry and continues the cycle.

    If there are no trash entries, stops the loop.
    The loop should be started again by when new entry is created in the trash.
    """

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        logger.debug("Starting automatic trash removal.")

        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(timeout=1)
            self._thread = None

    def _run(self) -> None:
        with session_factory() as db:
            # get the next item in queue for deletion
            trash_entry = db.scalar(select(DNSTrashInDB).order_by(DNSTrashInDB.deletion_timestamp.asc()).limit(1))

        if trash_entry is None:
            logger.debug("No items in trash. Stopping automatic trash removal.")
            return

        # calculate time to live for the next item in queue

        deletion_datetime = trash_entry.deletion_timestamp + timedelta(seconds=ITEM_TRASH_TIME_TO_LIVE_SECONDS)

        delay = (deletion_datetime - datetime.now(timezone.utc)).total_seconds()

        logger.debug("Next automatic deletion scheduled in %s seconds.", delay)

        if delay > 0:
            self._stop_event.wait(delay)

        if self._stop_event.is_set():
            return

        with session_factory() as db:
            trash_entry_in_db = db.get(DNSTrashInDB, trash_entry.entry_uuid)

            # if the trash entry still exists, permanently remove it
            if trash_entry_in_db is not None:
                trash_entry = TrashEntry.from_db(trash_entry_in_db)

                logger.info("Automatically deleting %s %s permanently.", trash_entry.object_type, trash_entry.object_data)

                db.delete(trash_entry_in_db)
                db.commit()

                create_log_entry(
                    db=db,
                    actor_type=ActorType.AUTOMATIC,
                    action=ChangeAction.PERMANENTLY_DELETED,
                    actor="system",
                    affected_object_type=trash_entry.object_type,
                    affected_object_name=trash_entry.object_data.name,
                    object_before=jsonable_encoder(trash_entry),
                    object_after=None,
                )

        self._thread = None
        self.start()


automatic_trash_removal = AutomaticTrashRemoval()

__all__ = ["automatic_trash_removal"]
