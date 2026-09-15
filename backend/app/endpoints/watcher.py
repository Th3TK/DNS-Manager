import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.management.watcher.authentication import authenticate_watcher
from app.management.watcher.watcher import watcher_delete, watcher_sync, watcher_update
from app.models.record import WatcherRecordForm, WatcherRecordsForm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/watcher", tags=["Watcher"])


@router.post("/update", status_code=status.HTTP_204_NO_CONTENT)
def __watcher_update_record__(
    db: Annotated[Session, Depends(get_db)],
    watcher_name: Annotated[str, Depends(authenticate_watcher)],
    form: WatcherRecordForm,
):
    watcher_update(
        db=db,
        record_name=form.record_name,
        content=form.content,
        watcher_name=watcher_name,
    )


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def __watcher_delete_record__(
    db: Annotated[Session, Depends(get_db)],
    watcher_name: Annotated[str, Depends(authenticate_watcher)],
    form: WatcherRecordForm,
):
    watcher_delete(
        db=db,
        record_name=form.record_name,
        content=form.content,
        watcher_name=watcher_name,
    )


@router.post("/sync", status_code=status.HTTP_204_NO_CONTENT)
def __watcher_synchronize_records__(
    db: Annotated[Session, Depends(get_db)],
    watcher_name: Annotated[str, Depends(authenticate_watcher)],
    form: WatcherRecordsForm,
):
    watcher_sync(
        db=db,
        record_names=form.record_names,
        content=form.content,
        watcher_name=watcher_name,
    )
