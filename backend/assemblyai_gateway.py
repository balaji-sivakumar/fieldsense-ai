"""Holds the backend's connection to the AssemblyAI Voice Agent API.

Per AssemblyAI's docs (fetched 2026-09-06), a server holding its own raw
API key can connect directly to the WS endpoint with an Authorization
header — the short-lived ?token= flow is only needed when a browser
connects directly (not our architecture: the backend is the only
component that talks to AssemblyAI, per CLAUDE.md).

No pre-created agent is used; session config is sent inline via
session.update right after connecting. Audio is 24kHz mono 16-bit PCM,
base64-encoded, in both directions.

M3: client-side function tools (not AssemblyAI's HTTP tools) — chosen
because HTTP tools require AssemblyAI's servers to reach our endpoint
over the public internet, which localhost can't do before M7
deployment, and because client-side tools keep the entire call/result
round trip inside this one WebSocket connection, matching both the
hackathon's "single connection" requirement and CLAUDE.md's rule that
the LLM only ever *decides* to call a tool — execution stays fully in
our own backend's control (tool_registry.dispatch, called from
voice_ws.py). See tool_schemas.py for the JSON-Schema tool definitions.
"""

import base64
import json
from typing import AsyncIterator, Optional

import websockets

from tool_schemas import TOOL_SCHEMAS

ASSEMBLYAI_WS_URL = "wss://agents.assemblyai.com/v1/ws"

SYSTEM_PROMPT = (
    "You are FieldSense, a voice assistant for industrial field technicians "
    "servicing air compressors. Keep responses to 1-2 sentences. Always use "
    "the available tools to look up real asset details, telemetry, "
    "maintenance history, manual guidance, and parts inventory rather than "
    "guessing — never invent asset data, readings, or manual guidance that "
    "didn't come back from a tool call.\n\n"
    "Safety classification: track the current risk level for this "
    "conversation and call set_risk_level whenever it changes (including "
    "back down to a less severe level). The levels, from README's safety "
    "model: observation (retrieving info, recording measurements) is the "
    "default; low_risk_inspection (guide an approved checklist one step at "
    "a time); lockout_required (require the technician to explicitly "
    "confirm the site's lockout/tagout procedure was completed AND "
    "independently verified before continuing — never proceed on a vague "
    "'yes' alone, and never claim that verbal confirmation proves the "
    "physical environment is actually safe); specialist_required (stop "
    "giving procedural/troubleshooting guidance and call "
    "escalate_to_specialist); dangerous_condition (immediately instruct the "
    "technician to move away from the equipment and follow the site's "
    "emergency procedure, then escalate). Manual guidance retrieved via "
    "search_manual may itself state when a condition requires escalation — "
    "follow it. Never give repair instructions beyond what a tool result "
    "supports, and never suggest the technician perform a lockout, repair, "
    "or other physical action themselves without following site procedure."
)
GREETING = "Hi, this is FieldSense. How can I help?"


def _as_function_tools() -> list[dict]:
    return [
        {
            "type": "function",
            "name": schema["name"],
            "description": schema["description"],
            "parameters": schema["parameters"],
            "execution_mode": "interactive",
            "timeout_seconds": 30,
        }
        for schema in TOOL_SCHEMAS
    ]


def build_session_update() -> dict:
    return {
        "type": "session.update",
        "session": {
            "system_prompt": SYSTEM_PROMPT,
            "greeting": GREETING,
            "tools": _as_function_tools(),
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

    async def send_tool_result(self, call_id: str, result: str, is_error: bool = False) -> None:
        message = {
            "type": "tool.result",
            "call_id": call_id,
            "result": result,
            "is_error": is_error,
        }
        await self._ws.send(json.dumps(message))

    async def events(self) -> AsyncIterator[dict]:
        async for raw in self._ws:
            yield json.loads(raw)

    async def close(self) -> None:
        if self._ws is not None:
            await self._ws.close()
