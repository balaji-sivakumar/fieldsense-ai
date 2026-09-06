import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # must run before database.py reads DATABASE_URL at import time

from dashboard_hub import dashboard_hub  # noqa: E402
from database import init_db  # noqa: E402
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
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


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
