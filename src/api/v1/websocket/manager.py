# src/api/v1/websocket/manager.py
from fastapi import WebSocket
from typing import Dict, Set
import asyncio


class ConnectionManager:
    """WebSocket connection manager."""

    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.connections:
            self.connections[channel] = set()
        self.connections[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.connections:
            self.connections[channel].discard(websocket)

    async def broadcast(self, channel: str, message: dict):
        """Send message to all clients in a channel."""
        if channel not in self.connections:
            return

        for websocket in self.connections[channel].copy():
            try:
                await websocket.send_json(message)
            except Exception:
                self.connections[channel].discard(websocket)


# Global instance
ws_manager = ConnectionManager()
