import asyncio
import logging
from datetime import datetime, timezone

from app.management.users.authentication import get_authenticated_user_from_token
from app.management.users.tokens import decode_token
from app.management.websocket.websocket_manager import global_websocket_manager
from app.models.user import User
from fastapi import HTTPException, WebSocketDisconnect, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket, WebSocketState

logger = logging.getLogger(__name__)


class WebSocketHandler(BaseModel):
    """
    Provides a base WebSocket handler.
    Handles authentication through access_token cookie and automatically closes the connection at token expiration.
    """

    websocket: WebSocket
    closer: asyncio.Task | None = None
    _user: User | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __hash__(self):
        return id(self.websocket)

    def __eq__(self, other):
        return self is other

    async def accept(self, db: Session) -> None:
        await self.websocket.accept()

        # try to get access_token
        access_token = self.websocket.cookies.get("access_token")

        if not access_token:
            await self.close(status.WS_1008_POLICY_VIOLATION, "Could not validate credentials.")
            return

        try:
            # retrieve user from the token, throws HTTPException if user is disabled/doesn't exist
            self._user = get_authenticated_user_from_token(db, access_token)

            await global_websocket_manager.register(self._user.username, self)

            # create future task for disconnecting when the token expires
            self.closer = asyncio.create_task(self.__close_at_token_expiration__(access_token))

        except HTTPException as exc:
            # close, unauthorized
            return await self.close(status.WS_1008_POLICY_VIOLATION, exc.detail)

        except Exception:
            await self.close(status.WS_1011_INTERNAL_ERROR, "Internal server error.")
            logger.exception("Exception occured in the WebsocketHandler.accept")

    async def __close_at_token_expiration__(self, access_token):
        """
        Disconnect the WebSocket when the token expires.
        """

        try:
            decoded_payload = decode_token(access_token)
            expiration_delay = max(0, (decoded_payload.expiration_date - datetime.now(timezone.utc)).total_seconds())

            if expiration_delay > 0:
                await asyncio.sleep(expiration_delay)

            await self.close(status.WS_1008_POLICY_VIOLATION, "Access token expired.")
        except asyncio.CancelledError, WebSocketDisconnect:
            # already disconnected
            pass
        except Exception:
            logger.exception("Exception occured in the WebsocketHandler's __close_at_token_expiration__ method")

    async def close(self, code: int = status.WS_1000_NORMAL_CLOSURE, reason: str | None = None) -> None:
        """
        Disconnects the WebSocket.
        """

        if self.closer is not None:
            self.closer.cancel()

        if self._user:
            await global_websocket_manager.unregister(self._user.username, self)

        try:
            if self.is_connected():
                await self.websocket.close(code, reason)
        except (RuntimeError, WebSocketDisconnect):
            # WebSocket already closed
            pass

    def is_connected(self) -> bool:
        return (
            self.websocket.application_state == WebSocketState.CONNECTED
            and self.websocket.client_state == WebSocketState.CONNECTED
        )
