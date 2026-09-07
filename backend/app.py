import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # must run before database.py reads DATABASE_URL at import time

import chroma_client  # noqa: E402
import database  # noqa: E402
import telemetry_simulator  # noqa: E402
from dashboard_hub import dashboard_hub  # noqa: E402
from tool_registry import dispatch  # noqa: E402
from voice_ws import handle_voice_websocket  # noqa: E402

app = FastAPI(title="FieldSense AI backend")

_allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    database.init_db()


@app.get("/health")
def health() -> dict:
    # AssemblyAI isn't live-pinged here — a real connection attempt costs
    # voice-minutes, and /health may be polled frequently by the host.
    # DB and Chroma checks are cheap (a trivial query / collection read).
    db_ok = database.check_connection()
    chroma_ok = chroma_client.check_connection()
    assemblyai_configured = bool(os.getenv("ASSEMBLYAI_API_KEY"))

    return {
        "status": "ok" if (db_ok and chroma_ok and assemblyai_configured) else "degraded",
        "database": "ok" if db_ok else "unreachable",
        "manual_search": "ok" if chroma_ok else "unreachable",
        "voice": "configured" if assemblyai_configured else "not configured",
    }


@app.get("/assets/{asset_id}")
async def get_asset(asset_id: str) -> dict:
    result = await dispatch("get_asset_details", {"asset_id": asset_id}, session_id="rest")
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["error"])
    return result["result"]


@app.post("/tools/get_live_telemetry")
async def tool_get_live_telemetry(payload: dict) -> dict:
    return await dispatch("get_live_telemetry", payload, session_id="rest")


@app.post("/tools/get_maintenance_history")
async def tool_get_maintenance_history(payload: dict) -> dict:
    return await dispatch("get_maintenance_history", payload, session_id="rest")


@app.post("/tools/search_manual")
async def tool_search_manual(payload: dict) -> dict:
    return await dispatch("search_manual", payload, session_id="rest")


@app.post("/tools/check_parts_inventory")
async def tool_check_parts_inventory(payload: dict) -> dict:
    return await dispatch("check_parts_inventory", payload, session_id="rest")


@app.post("/tools/create_work_order")
async def tool_create_work_order(payload: dict) -> dict:
    return await dispatch("create_work_order", payload, session_id="rest")


@app.post("/tools/record_observation")
async def tool_record_observation(payload: dict) -> dict:
    return await dispatch("record_observation", payload, session_id="rest")


@app.post("/tools/escalate_to_specialist")
async def tool_escalate_to_specialist(payload: dict) -> dict:
    return await dispatch("escalate_to_specialist", payload, session_id="rest")


@app.post("/tools/complete_work_order")
async def tool_complete_work_order(payload: dict) -> dict:
    return await dispatch("complete_work_order", payload, session_id="rest")


@app.get("/simulator/scenarios")
def list_scenarios() -> dict:
    return {"scenarios": sorted(telemetry_simulator.SCENARIOS)}


@app.get("/simulator/scenario/{asset_id}")
def get_scenario(asset_id: str) -> dict:
    return {"asset_id": asset_id, "scenario": telemetry_simulator.get_scenario(asset_id)}


@app.post("/simulator/scenario")
async def set_scenario(payload: dict) -> dict:
    asset_id = payload.get("asset_id")
    scenario = payload.get("scenario")
    if not asset_id or not scenario:
        raise HTTPException(status_code=400, detail="asset_id and scenario are required")
    try:
        telemetry_simulator.set_scenario(asset_id, scenario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    await dashboard_hub.broadcast({"type": "scenario_change", "asset_id": asset_id, "scenario": scenario})
    return {"asset_id": asset_id, "scenario": scenario}


@app.websocket("/ws/voice")
async def ws_voice(websocket: WebSocket) -> None:
    await handle_voice_websocket(websocket)


@app.websocket("/ws/dashboard")
async def ws_dashboard(websocket: WebSocket) -> None:
    await dashboard_hub.connect(websocket)
    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
    except WebSocketDisconnect:
        pass
    finally:
        dashboard_hub.disconnect(websocket)
