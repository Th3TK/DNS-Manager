import logging

from app.management.status_check.status_check import automatic_status_check
from app.management.status_check.websocket_manager import status_check_websocket_manager
from app.management.websocket.websocket_handler import WebSocketHandler
from fastapi import WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)


class StatusCheckWebSocketHandler(WebSocketHandler):
    async def listen(self):

        await status_check_websocket_manager.register(self)

        try:
            data = automatic_status_check.get_data()

            if data is not None:
                await self.websocket.send_json(jsonable_encoder(data))

            while self.is_connected():
                await self.websocket.receive()
                # keep open connection while ignoring any incoming messages
        except WebSocketDisconnect:
            await status_check_websocket_manager.unregister(self)
            pass
        except Exception:
            logging.exception(f"Unhandled expection within websocket {self.websocket}.")
