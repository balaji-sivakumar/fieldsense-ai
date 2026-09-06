"""Central tool dispatch.

Validates every call against its JSON Schema (tool_schemas.py), executes
it with a timeout, records an audit event, and broadcasts it to the
judge-facing dashboard. This is the single chokepoint both the REST
/tools/* endpoints and the AssemblyAI voice loop call through, so every
tool invocation is audited and visible on the dashboard regardless of
where it came from.
"""

import asyncio
import json

import jsonschema

from dashboard_hub import dashboard_hub
from database import SessionLocal
from models import ToolAuditLog
from tool_schemas import TOOL_SCHEMAS_BY_NAME
from tools.asset_tools import get_asset_details
from tools.maintenance_tools import get_maintenance_history
from tools.manual_tools import search_manual
from tools.parts_tools import check_parts_inventory
from tools.telemetry_tools import get_live_telemetry
from tools.work_order_tools import (
    complete_work_order,
    create_work_order,
    escalate_to_specialist,
    record_observation,
)

TOOLS = {
    "get_asset_details": get_asset_details,
    "get_live_telemetry": get_live_telemetry,
    "get_maintenance_history": get_maintenance_history,
    "search_manual": search_manual,
    "check_parts_inventory": check_parts_inventory,
    "create_work_order": create_work_order,
    "record_observation": record_observation,
    "escalate_to_specialist": escalate_to_specialist,
    "complete_work_order": complete_work_order,
}

TOOL_TIMEOUT_SECONDS = 10


async def dispatch(tool_name: str, args: dict, session_id: str = "unknown") -> dict:
    schema = TOOL_SCHEMAS_BY_NAME.get(tool_name)
    tool_fn = TOOLS.get(tool_name)
    if schema is None or tool_fn is None:
        result = {"status": "error", "error": f"unknown tool: {tool_name}"}
        await _record(tool_name, args, result, session_id)
        return result

    try:
        jsonschema.validate(args, schema["parameters"])
    except jsonschema.ValidationError as exc:
        result = {"status": "error", "error": f"invalid arguments: {exc.message}"}
        await _record(tool_name, args, result, session_id)
        return result

    try:
        raw_result = await asyncio.wait_for(asyncio.to_thread(tool_fn, **args), timeout=TOOL_TIMEOUT_SECONDS)
        result = {"status": "ok", "result": raw_result}
    except asyncio.TimeoutError:
        result = {"status": "error", "error": f"{tool_name} timed out after {TOOL_TIMEOUT_SECONDS}s"}
    except (TypeError, ValueError) as exc:
        result = {"status": "error", "error": str(exc)}

    await _record(tool_name, args, result, session_id)
    return result


async def _record(tool_name: str, args: dict, result: dict, session_id: str) -> None:
    db = SessionLocal()
    try:
        db.add(
            ToolAuditLog(
                tool_name=tool_name,
                args_json=json.dumps(args),
                status=result.get("status", "unknown"),
                session_id=session_id,
            )
        )
        db.commit()
    finally:
        db.close()

    await dashboard_hub.broadcast(
        {
            "type": "tool_call",
            "tool_name": tool_name,
            "args": args,
            "result": result,
            "session_id": session_id,
        }
    )
