import json

import audit_log
from database import SessionLocal
from models import WorkOrder, WorkOrderEvent
from tools.asset_tools import get_asset_details
from tools.maintenance_tools import get_maintenance_history
from tools.telemetry_tools import get_live_telemetry


def create_work_order(asset_id: str, problem: str, priority: str = "normal") -> dict:
    get_asset_details(asset_id)  # raises ValueError if unknown

    db = SessionLocal()
    try:
        work_order = WorkOrder(asset_id=asset_id, problem=problem, priority=priority, status="open")
        db.add(work_order)
        db.commit()
        db.refresh(work_order)
        return {
            "work_order_id": work_order.id,
            "asset_id": work_order.asset_id,
            "problem": work_order.problem,
            "priority": work_order.priority,
            "status": work_order.status,
        }
    finally:
        db.close()


def _get_work_order_or_raise(db, work_order_id: int) -> WorkOrder:
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if work_order is None:
        raise ValueError(f"unknown work_order_id: {work_order_id}")
    return work_order


def record_observation(work_order_id: int, measurement: str, value: float, unit: str) -> dict:
    db = SessionLocal()
    try:
        _get_work_order_or_raise(db, work_order_id)  # raises ValueError if unknown
        db.add(
            WorkOrderEvent(
                work_order_id=work_order_id,
                event_type="observation",
                detail=json.dumps({"measurement": measurement, "value": value, "unit": unit}),
            )
        )
        db.commit()
        return {
            "work_order_id": work_order_id,
            "recorded": {"measurement": measurement, "value": value, "unit": unit},
        }
    finally:
        db.close()


def complete_work_order(work_order_id: int, resolution: str) -> dict:
    db = SessionLocal()
    try:
        work_order = _get_work_order_or_raise(db, work_order_id)
        work_order.status = "completed"
        work_order.resolution = resolution
        db.add(WorkOrderEvent(work_order_id=work_order_id, event_type="completed", detail=resolution))
        db.commit()
        return {"work_order_id": work_order_id, "status": "completed", "resolution": resolution}
    finally:
        db.close()


def escalate_to_specialist(
    asset_id: str, reason: str, work_order_id: int | None = None, session_id: str = "unknown"
) -> dict:
    """Structured specialist handover (README: "asset, symptoms, readings,
    history, sources, and actions already taken"). session_id is injected
    by tool_registry.dispatch() (not part of this tool's JSON Schema — the
    LLM never supplies it) so the handover can cite this session's actual
    tool-call history rather than guessing or re-deriving it.
    """
    asset = get_asset_details(asset_id)  # raises ValueError if unknown
    telemetry = get_live_telemetry(asset_id)
    history = get_maintenance_history(asset_id)

    db = SessionLocal()
    try:
        if work_order_id is not None:
            _get_work_order_or_raise(db, work_order_id)  # raises ValueError if unknown
            db.add(WorkOrderEvent(work_order_id=work_order_id, event_type="escalated", detail=reason))
            db.commit()
    finally:
        db.close()

    return {
        "asset_id": asset_id,
        "reason": reason,
        "work_order_id": work_order_id,
        "escalated": True,
        "risk_tier": "specialist_required",
        "handover": {
            "asset": asset,
            "current_telemetry": telemetry,
            "maintenance_history": history["records"],
            "manual_sources": audit_log.recent_manual_sources(session_id),
            "actions_already_taken": audit_log.recent_actions(session_id),
        },
    }
