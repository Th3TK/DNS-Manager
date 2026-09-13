import asyncio
import logging
from typing import TYPE_CHECKING

from fastapi import WebSocketDisconnect
from uvicorn.protocols.utils import ClientDisconnected

if TYPE_CHECKING:
    from app.management.status_check.websocket_handler import StatusCheckWebSocketHandler

logger = logging.getLogger(__name__)


class StatusCheckWebSocketManager:
    """
    Manages all status check websockets and handles the status check update broadcast.
    """

    def __init__(self):
        self._connections: set["StatusCheckWebSocketHandler"] = set()
        self._lock = asyncio.Lock()

    async def register(self, handler: "StatusCheckWebSocketHandler"):
        async with self._lock:
            self._connections.add(handler)

    async def unregister(self, handler: "StatusCheckWebSocketHandler"):
        async with self._lock:
            self._connections.discard(handler)

    async def broadcast(self, data):
        async with self._lock:
            handlers = list(self._connections)

        results = await asyncio.gather(
            *(handler.websocket.send_json(data) for handler in handlers),
            return_exceptions=True,
        )

        async with self._lock:
            for handler, result in zip(handlers, results):
                if isinstance(result, (WebSocketDisconnect, ClientDisconnected, RuntimeError)):
                    self._connections.discard(handler)
                    continue

                if isinstance(result, Exception):
                    logger.exception(
                        "Failed to send WebSocket data to %s",
                        handler,
                        exc_info=result,
                    )


status_check_websocket_manager = StatusCheckWebSocketManager()

__all__ = ["status_check_websocket_manager"]
