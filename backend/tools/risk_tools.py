"""set_risk_level: the LLM's only way to change a session's risk tier.

Not one of README's original 9 tools — added in M6 because the safety
model requires risk classification to be tracked, and (per the
LLM-decides/backend-executes boundary established in M3) the cleanest
way to do that is the same pattern as every other tool: the agent
declares its judgment via a tool call, the backend records and
displays it. voice_ws.py reads the "risk_tier" key from this tool's
result to update the session and notify the browser/dashboard —
escalate_to_specialist does the same implicitly (see work_order_tools.py).
"""

from session_manager import RISK_TIERS


def set_risk_level(level: str, reason: str) -> dict:
    if level not in RISK_TIERS:
        raise ValueError(f"unknown risk level: {level} (choices: {RISK_TIERS})")
    return {"risk_tier": level, "reason": reason}
