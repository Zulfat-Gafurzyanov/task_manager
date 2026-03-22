from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.ws.manager import manager

ws_router = APIRouter()


@ws_router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# const ws = new WebSocket("ws://localhost:8001/ws/1")
# ws.onopen = () => console.log("подключился!")
# ws.onmessage = (e) => console.log(JSON.parse(e.data))
