import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self._connections[user_id] = websocket
        logger.info("WS: user #%s подключился", user_id)

    def disconnect(self, user_id: int):
        self._connections.pop(user_id, None)
        logger.info("WS: user #%s отключился", user_id)

    async def send_to_user(self, user_id: int, message: dict):
        websocket = self._connections.get(user_id)
        if websocket:
            await websocket.send_json(message)
        else:
            logger.debug("WS: user #%s не подключён, уведомление пропущено", user_id)


manager = ConnectionManager()
