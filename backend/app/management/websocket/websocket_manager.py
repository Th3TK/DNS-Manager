import asyncio
from typing import TYPE_CHECKING

from fastapi import status

if TYPE_CHECKING:
    from app.management.websocket.websocket_handler import WebSocketHandler


class _WebSocketManager:
    def __init__(self):
        self._connections: dict[str, set["WebSocketHandler"]] = dict()
        self._lock = asyncio.Lock()

    async def register(self, username: str, handler: "WebSocketHandler"):
        async with self._lock:
            self._connections.setdefault(username, set()).add(handler)

    async def unregister(self, username: str, handler: "WebSocketHandler"):
        async with self._lock:
            if username in self._connections:
                self._connections[username].discard(handler)
                if not self._connections[username]:
                    del self._connections[username]

    async def disconnect_user(self, username: str, code: int = status.WS_1008_POLICY_VIOLATION, reason: str = "Account deleted"):
        handlers = list(self._connections.get(username, []))

        for handler in handlers:
            await handler.close(code, reason)


global_websocket_manager = _WebSocketManager()

__all__ = ["global_websocket_manager"]
