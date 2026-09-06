"""Holds the backend's connection to the AssemblyAI Voice Agent API.

Per AssemblyAI's docs (fetched 2026-09-06), a server holding its own raw
API key can connect directly to the WS endpoint with an Authorization
header — the short-lived ?token= flow is only needed when a browser
connects directly (not our architecture: the backend is the only
component that talks to AssemblyAI, per CLAUDE.md).

No pre-created agent is used; session config is sent inline via
session.update right after connecting. Audio is 24kHz mono 16-bit PCM,
base64-encoded, in both directions.

M2 scope: no tools registered yet (session has none). M3 will decide
between AssemblyAI's HTTP tools (server-to-server, AssemblyAI calls our
REST endpoints directly) and client-side tool.call/tool.result relayed
through this gateway.
"""

import base64
import json
from typing import AsyncIterator, Optional

import websockets

ASSEMBLYAI_WS_URL = "wss://agents.assemblyai.com/v1/ws"

SYSTEM_PROMPT = (
    "You are FieldSense, a voice assistant for industrial field "
    "technicians servicing air compressors. Keep responses to 1-2 "
    "sentences. You do not yet have access to real asset data."
)
GREETING = "Hi, this is FieldSense. How can I help?"


def build_session_update() -> dict:
    return {
        "type": "session.update",
        "session": {
            "system_prompt": SYSTEM_PROMPT,
            "greeting": GREETING,
            "input": {"format": {"encoding": "audio/pcm"}},
            "output": {"format": {"encoding": "audio/pcm"}},
        },
    }


class AssemblyAIGateway:
    """One AssemblyAI Voice Agent API session for one technician connection."""

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._ws: Optional[websockets.WebSocketClientProtocol] = None

    async def connect(self) -> None:
        self._ws = await websockets.connect(
            ASSEMBLYAI_WS_URL,
            extra_headers={"Authorization": f"Bearer {self._api_key}"},
        )
        await self._ws.send(json.dumps(build_session_update()))

    async def send_audio(self, pcm_bytes: bytes) -> None:
        message = {
            "type": "input.audio",
            "audio": base64.b64encode(pcm_bytes).decode("ascii"),
        }
        await self._ws.send(json.dumps(message))

    async def events(self) -> AsyncIterator[dict]:
        async for raw in self._ws:
            yield json.loads(raw)

    async def close(self) -> None:
        if self._ws is not None:
            await self._ws.close()
