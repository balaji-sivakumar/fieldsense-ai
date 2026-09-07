"""Per-technician voice session state.

M6: adds risk_tier, set by voice_ws.py whenever a tool result carries
a "risk_tier" field (set_risk_level, escalate_to_specialist). Active
work order tracking is not needed — work_order_id already flows
through tool arguments/results, and every tool call is independently
auditable via tool_audit_log.
"""

import uuid
from dataclasses import dataclass

# Order matches README's safety model table (least to most severe).
RISK_TIERS = [
    "observation",
    "low_risk_inspection",
    "lockout_required",
    "specialist_required",
    "dangerous_condition",
]
DEFAULT_RISK_TIER = "observation"


@dataclass
class VoiceSession:
    session_id: str
    state: str = "connecting"  # connecting|ready|listening|thinking|speaking|error|closed
    risk_tier: str = DEFAULT_RISK_TIER


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, VoiceSession] = {}

    def create(self) -> VoiceSession:
        session = VoiceSession(session_id=str(uuid.uuid4()))
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> VoiceSession | None:
        return self._sessions.get(session_id)

    def remove(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


session_manager = SessionManager()
