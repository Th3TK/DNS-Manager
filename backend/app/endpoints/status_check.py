from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.management.status_check.websocket_handler import StatusCheckWebSocketHandler

router = APIRouter(tags=["Record Status Check"])


@router.websocket("/status-check")
async def status_websocket(websocket: WebSocket, db: Annotated[Session, Depends(get_db)]):
    handler = StatusCheckWebSocketHandler(websocket=websocket)

    await handler.accept(db)
    await handler.listen()
