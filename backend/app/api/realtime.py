from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, device_id: str | None = None) -> None:
    hub = websocket.app.state.realtime_hub
    await hub.connect(websocket, device_id)
    try:
        while True:
            message = await websocket.receive_text()
            if message == 'ping':
                await websocket.send_json({'type': 'pong'})
    except WebSocketDisconnect:
        hub.disconnect(websocket)
