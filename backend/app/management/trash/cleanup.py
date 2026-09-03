import asyncio
import logging
from asyncio import Task
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
    def __init__(self):
        self._task: Task[None] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    async def initialize(self) -> None:
        self._loop = asyncio.get_running_loop()

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            logger.debug("Automatic trash removal already running.")
            return

        if self._loop is None:
            raise RuntimeError("AutomaticTrashRemoval has not been initialized")

        logger.debug("Starting automatic trash removal.")
        self._loop.call_soon_threadsafe(self._schedule)

    def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            self._task = None

    def _schedule(self) -> None:
        if self._task is not None and not self._task.done():
            return

        self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        with session_factory() as db:
            trash_entry = db.scalar(select(DNSTrashInDB).order_by(DNSTrashInDB.deletion_timestamp.asc()).limit(1))

        if trash_entry is None:
            logger.debug("No items in trash. Stopping automatic trash removal.")
            return

        deletion_datetime = trash_entry.deletion_timestamp + timedelta(seconds=ITEM_TRASH_TIME_TO_LIVE_SECONDS)

        delay = (deletion_datetime - datetime.now(timezone.utc)).total_seconds()

        logger.debug("Next automatic deletion scheduled in %s seconds.", delay)

        if delay > 0:
            await asyncio.sleep(delay)

        with session_factory() as db:
            trash_entry_in_db = db.get(DNSTrashInDB, trash_entry.entry_uuid)

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

        self._task = None
        self._schedule()


automatic_trash_removal = AutomaticTrashRemoval()

__all__ = ["automatic_trash_removal"]
