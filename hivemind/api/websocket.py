"""WebSocket endpoint for live debate streaming."""

from __future__ import annotations
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set


class DebateStream:
    """Manages WebSocket connections for live debate streaming."""

    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, debate_id: str):
        await websocket.accept()
        if debate_id not in self.connections:
            self.connections[debate_id] = set()
        self.connections[debate_id].add(websocket)

    def disconnect(self, websocket: WebSocket, debate_id: str):
        if debate_id in self.connections:
            self.connections[debate_id].discard(websocket)
            if not self.connections[debate_id]:
                del self.connections[debate_id]

    async def broadcast(self, debate_id: str, data: dict):
        if debate_id in self.connections:
            dead = set()
            for ws in self.connections[debate_id]:
                try:
                    await ws.send_json(data)
                except:
                    dead.add(ws)
            for ws in dead:
                self.connections[debate_id].discard(ws)


stream = DebateStream()
