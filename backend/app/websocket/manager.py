"""
WebSocket Connection Manager and Broadcaster for WiFiSense AI.
"""

from typing import List, Dict, Any, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger("wifisense.websocket")


class ConnectionManager:
    """Manages active WebSocket client connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_json(self, data: Dict[str, Any]):
        """Broadcasts payload to all connected clients asynchronously."""
        if not self.active_connections:
            return
        dead_connections = set()
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.warning(f"Failed to send to client, removing: {e}")
                dead_connections.add(connection)

        for dead in dead_connections:
            if dead in self.active_connections:
                self.active_connections.remove(dead)


manager = ConnectionManager()
