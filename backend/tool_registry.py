"""Central tool dispatch.

M1 scope: plain Python functions, no JSON-Schema validation, no
AssemblyAI wiring. M3 adds strict schema validation for every tool
below and connects `dispatch` to AssemblyAI's tool.call/tool.result
events — this module's shape is built now so M3 only has to add
validation, not build the registry itself.
"""

from tools.asset_tools import get_asset_details
from tools.manual_tools import search_manual
from tools.telemetry_tools import get_live_telemetry
from tools.work_order_tools import create_work_order

TOOLS = {
    "get_asset_details": get_asset_details,
    "get_live_telemetry": get_live_telemetry,
    "search_manual": search_manual,
    "create_work_order": create_work_order,
}


def dispatch(tool_name: str, args: dict) -> dict:
    tool = TOOLS.get(tool_name)
    if tool is None:
        return {"status": "error", "error": f"unknown tool: {tool_name}"}

    try:
        result = tool(**args)
        return {"status": "ok", "result": result}
    except (TypeError, ValueError) as exc:
        return {"status": "error", "error": str(exc)}
