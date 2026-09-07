"""Read-side helper over tool_audit_log, for building the specialist
handover in tools/work_order_tools.py — the only current consumer.
"""

import json

from database import SessionLocal
from models import ToolAuditLog


def recent_actions(session_id: str, limit: int = 8) -> list[dict]:
    db = SessionLocal()
    try:
        rows = (
            db.query(ToolAuditLog)
            .filter(ToolAuditLog.session_id == session_id)
            .order_by(ToolAuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "tool_name": row.tool_name,
                "args": json.loads(row.args_json),
                "status": row.status,
                "timestamp": row.timestamp.isoformat(),
            }
            for row in rows
        ]
    finally:
        db.close()


def recent_manual_sources(session_id: str, limit: int = 3) -> list[dict]:
    db = SessionLocal()
    try:
        rows = (
            db.query(ToolAuditLog)
            .filter(
                ToolAuditLog.session_id == session_id,
                ToolAuditLog.tool_name == "search_manual",
                ToolAuditLog.status == "ok",
            )
            .order_by(ToolAuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        sources = []
        for row in rows:
            if not row.result_json:
                continue
            body = json.loads(row.result_json).get("result", {})
            if body.get("found"):
                sources.append(
                    {"document": body.get("document"), "section": body.get("section"), "page": body.get("page")}
                )
        return sources
    finally:
        db.close()
