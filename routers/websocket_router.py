from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager

router = APIRouter(
    tags=["WebSocket"]
)

@router.websocket("/ws/match/{match_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: int):
    """
    This is the endpoint your Flutter app connects to.
    It simply handles the connection lifecycle.
    """
    await manager.connect(websocket, match_id)
    try:
        while True:
            # Keep the connection alive.
            # You can also listen for messages from the client if needed.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, match_id)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        manager.disconnect(websocket, match_id)