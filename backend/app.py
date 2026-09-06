import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from tool_registry import dispatch

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
def get_asset(asset_id: str) -> dict:
    result = dispatch("get_asset_details", {"asset_id": asset_id})
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["error"])
    return result["result"]


@app.post("/tools/get_live_telemetry")
def tool_get_live_telemetry(payload: dict) -> dict:
    return dispatch("get_live_telemetry", payload)


@app.post("/tools/search_manual")
def tool_search_manual(payload: dict) -> dict:
    return dispatch("search_manual", payload)


@app.post("/tools/create_work_order")
def tool_create_work_order(payload: dict) -> dict:
    return dispatch("create_work_order", payload)
