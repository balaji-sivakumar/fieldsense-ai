"""In-memory hub for the judge-facing dashboard's live event feed.

Every tool call, from any source (voice session or REST), is broadcast
here by tool_registry.dispatch() so the dashboard shows a live,
unified feed regardless of how the call was triggered.
"""

from fastapi import WebSocket


class DashboardHub:
    def __init__(self) -> None:
        self._sockets: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._sockets.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._sockets.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        dead = []
        for socket in self._sockets:
            try:
                await socket.send_json(message)
            except Exception:
                dead.append(socket)
        for socket in dead:
            self._sockets.discard(socket)


dashboard_hub = DashboardHub()
