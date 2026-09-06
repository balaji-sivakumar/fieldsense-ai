"""/ws/voice: relays audio and events between the browser and AssemblyAI.

Protocol with the browser:
- browser -> backend: raw binary frames (PCM16 mono, 24kHz)
- backend -> browser: JSON text frames — {"type": "state", "value": ...},
  transcript events, {"type": "audio", "data": <base64 PCM16>}, or
  {"type": "error", "message": ...}
"""

import asyncio
import json
import logging
import os

from fastapi import WebSocket, WebSocketDisconnect

from assemblyai_gateway import AssemblyAIGateway
from session_manager import session_manager
from tool_registry import dispatch

logger = logging.getLogger("voice_ws")

_STATE_BY_EVENT = {
    "session.ready": "ready",
    "input.speech.started": "listening",
    "input.speech.stopped": "thinking",
    "reply.started": "speaking",
    "reply.done": "listening",
}


def _translate_event(event: dict) -> dict | None:
    event_type = event.get("type")

    if event_type in _STATE_BY_EVENT:
        return {"type": "state", "value": _STATE_BY_EVENT[event_type]}
    if event_type == "transcript.user.delta":
        return {"type": "transcript.user.delta", "text": event.get("text", "")}
    if event_type == "transcript.user":
        return {"type": "transcript.user", "text": event.get("text", "")}
    if event_type == "reply.audio":
        return {"type": "audio", "data": event.get("data", "")}
    if event_type == "transcript.agent.delta":
        return {"type": "transcript.agent.delta", "text": event.get("delta", "")}
    if event_type == "transcript.agent":
        return {
            "type": "transcript.agent",
            "text": event.get("text", ""),
            "interrupted": event.get("interrupted", False),
        }
    if event_type == "session.error":
        return {"type": "error", "message": event.get("message", "unknown AssemblyAI error")}
    if event_type == "session.ended":
        return {"type": "ended"}
    return None


async def handle_voice_websocket(websocket: WebSocket) -> None:
    await websocket.accept()

    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        await websocket.send_json({"type": "error", "message": "ASSEMBLYAI_API_KEY not configured"})
        await websocket.close()
        return

    session = session_manager.create()
    gateway = AssemblyAIGateway(api_key)

    try:
        await gateway.connect()
    except Exception as exc:
        logger.exception("failed to connect to AssemblyAI")
        await websocket.send_json({"type": "error", "message": f"failed to connect to AssemblyAI: {exc}"})
        await websocket.close()
        session_manager.remove(session.session_id)
        return

    async def pump_browser_to_assemblyai() -> None:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
            data = message.get("bytes")
            if data is not None:
                await gateway.send_audio(data)

    async def pump_assemblyai_to_browser() -> None:
        # AssemblyAI's protocol requires tool.result to be sent only after
        # reply.done is the latest received event (so the agent finishes
        # its current turn, e.g. "one moment while I check...", before the
        # tool result triggers a new turn) — so results are queued here and
        # flushed on reply.done rather than sent immediately on tool.call.
        pending_tool_results: list[dict] = []

        async for event in gateway.events():
            event_type = event.get("type")

            if event_type == "tool.call":
                call_id = event.get("call_id")
                name = event.get("name")
                arguments = event.get("arguments") or {}
                result = await dispatch(name, arguments, session_id=session.session_id)
                pending_tool_results.append(
                    {
                        "call_id": call_id,
                        "result": json.dumps(result),
                        "is_error": result.get("status") == "error",
                    }
                )
                continue

            translated = _translate_event(event)
            if translated is not None:
                try:
                    await websocket.send_json(translated)
                except (WebSocketDisconnect, RuntimeError):
                    # Browser disconnected between the last received frame
                    # and this send — benign race, not a session error.
                    return

            if event_type == "reply.done" and pending_tool_results:
                for pending in pending_tool_results:
                    await gateway.send_tool_result(**pending)
                pending_tool_results.clear()

    tasks = [
        asyncio.create_task(pump_browser_to_assemblyai()),
        asyncio.create_task(pump_assemblyai_to_browser()),
    ]
    try:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        # One side finished or failed — cancel the other rather than leaving
        # it running (which would otherwise keep a billed AssemblyAI session
        # open with no browser attached, or keep streaming audio into a
        # closed gateway).
        for task in pending:
            task.cancel()
        for task in pending:
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
        for task in done:
            exc = task.exception()
            if exc is not None and not isinstance(exc, WebSocketDisconnect):
                raise exc
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.exception("voice session error")
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        try:
            await gateway.close()
        except Exception:
            logger.exception("error closing AssemblyAI gateway")
        try:
            await websocket.close()
        except Exception:
            pass
        session_manager.remove(session.session_id)
