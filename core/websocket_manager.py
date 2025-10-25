from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        # A dictionary to store connections, mapping match_id to a list of websockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, match_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        if match_id not in self.active_connections:
            self.active_connections[match_id] = []
        self.active_connections[match_id].append(websocket)
        print(f"New connection for match {match_id}. Total: {len(self.active_connections[match_id])}")

    def disconnect(self, websocket: WebSocket, match_id: int):
        """Disconnect a WebSocket."""
        if match_id in self.active_connections:
            self.active_connections[match_id].remove(websocket)
            print(f"Connection for match {match_id} closed. Total: {len(self.active_connections[match_id])}")

    async def broadcast_to_match(self, match_id: int, data: dict):
        """Send a JSON message to all clients watching a specific match."""
        if match_id in self.active_connections:
            for connection in self.active_connections[match_id]:
                await connection.send_json(data)

# Create a single, shared instance of the manager
manager = ConnectionManager()