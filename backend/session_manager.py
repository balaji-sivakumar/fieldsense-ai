"""Per-technician voice session state.

M2 scope: just enough to track that a session exists and its connection
state. M6 extends this with risk classification and active work order,
per architecture.md.
"""

import uuid
from dataclasses import dataclass


@dataclass
class VoiceSession:
    session_id: str
    state: str = "connecting"  # connecting|ready|listening|thinking|speaking|error|closed


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
