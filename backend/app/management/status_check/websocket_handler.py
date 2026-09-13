import logging

from app.management.status_check.status_check import automatic_status_check
from app.management.status_check.websocket_manager import status_check_websocket_manager
from app.management.websocket.websocket_handler import WebSocketHandler
from fastapi import WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)


class StatusCheckWebSocketHandler(WebSocketHandler):
    """
    Extends WebSocketHandler

    Handles status check websockets.
    On connect retrieves the cached status data and sends it instantly to the client.
    """

    async def listen(self):

        await status_check_websocket_manager.register(self)

        try:
            data = automatic_status_check.get_data()

            if data is not None:
                await self.websocket.send_json(jsonable_encoder(data))

            while self.is_connected():
                await self.websocket.receive()
                # keep open connection while ignoring any incoming messages
        except WebSocketDisconnect, RuntimeError:
            pass
        except Exception:
            logging.exception(f"Unhandled expection within websocket {self.websocket}.")
        finally:
            await status_check_websocket_manager.unregister(self)
            await self.close()
