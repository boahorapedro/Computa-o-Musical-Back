# src/api/v1/websocket/router.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.v1.websocket.manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/project/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: str):
    """WebSocket to track project status."""
    await manager.connect(websocket, f"project:{project_id}")

    try:
        while True:
            # Keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"project:{project_id}")


@router.websocket("/ws/mix/{mix_id}")
async def mix_websocket(websocket: WebSocket, mix_id: str):
    """WebSocket to track mix status."""
    await manager.connect(websocket, f"mix:{mix_id}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"mix:{mix_id}")
