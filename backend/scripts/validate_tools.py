"""Smoke-test every tool against a running backend, over real HTTP.

Distinct from tests/test_tools.py (which calls tool_registry.dispatch()
directly, in-process, against an isolated test DB): this script hits the
actual /assets and /tools/* REST endpoints on a live server, the same
way a REST client would. Useful for a quick end-to-end sanity check
after starting the backend, without needing pytest or a browser.

Usage:
    source venv/bin/activate
    python scripts/validate_tools.py
    # or against a different host:
    BACKEND_URL=http://localhost:8000 python scripts/validate_tools.py
"""

import json
import os
import sys
import urllib.error
import urllib.request

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
ASSET_ID = "AC-104"
SITE_ID = "SITE-01"
PART_NUMBER = "FLT-200"

_results: list[tuple[str, bool, str]] = []


def call(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    url = f"{BACKEND_URL}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def check(name: str, condition: bool, detail: str) -> None:
    _results.append((name, condition, detail))
    mark = "PASS" if condition else "FAIL"
    print(f"[{mark}] {name}: {detail}")


def main() -> None:
    status, body = call("GET", "/health")
    check("health", status == 200 and body.get("status") == "ok", str(body))

    status, body = call("GET", f"/assets/{ASSET_ID}")
    check("get_asset_details (known)", status == 200 and body.get("model") == "ACX-200", str(body))

    status, body = call("GET", "/assets/AC-999")
    check("get_asset_details (unknown -> 404)", status == 404, str(body))

    status, body = call("POST", "/tools/get_live_telemetry", {"asset_id": ASSET_ID})
    check(
        "get_live_telemetry",
        status == 200 and body.get("status") == "ok" and "temperature_f" in body.get("result", {}),
        str(body),
    )

    status, body = call("POST", "/tools/get_maintenance_history", {"asset_id": ASSET_ID})
    check(
        "get_maintenance_history",
        status == 200 and body.get("status") == "ok" and len(body.get("result", {}).get("records", [])) > 0,
        str(body),
    )

    status, body = call("POST", "/tools/search_manual", {"asset_model": "ACX-200", "fault_code": "E27"})
    check("search_manual", status == 200 and body.get("status") == "ok", str(body))

    status, body = call("POST", "/tools/check_parts_inventory", {"site_id": SITE_ID, "part_number": PART_NUMBER})
    check(
        "check_parts_inventory (found)",
        status == 200 and body.get("status") == "ok" and body.get("result", {}).get("found") is True,
        str(body),
    )

    status, body = call("POST", "/tools/create_work_order", {"asset_id": ASSET_ID, "problem": "validation run", "priority": "low"})
    work_order_id = body.get("result", {}).get("work_order_id")
    check("create_work_order", status == 200 and body.get("status") == "ok" and work_order_id is not None, str(body))

    status, body = call(
        "POST",
        "/tools/record_observation",
        {"work_order_id": work_order_id, "measurement": "motor_temperature", "value": 105.0, "unit": "F"},
    )
    check("record_observation", status == 200 and body.get("status") == "ok", str(body))

    status, body = call(
        "POST", "/tools/escalate_to_specialist", {"asset_id": ASSET_ID, "reason": "validation run", "work_order_id": work_order_id}
    )
    check(
        "escalate_to_specialist",
        status == 200 and body.get("status") == "ok" and body.get("result", {}).get("escalated") is True,
        str(body),
    )

    status, body = call(
        "POST", "/tools/complete_work_order", {"work_order_id": work_order_id, "resolution": "validation run complete"}
    )
    check(
        "complete_work_order",
        status == 200 and body.get("status") == "ok" and body.get("result", {}).get("status") == "completed",
        str(body),
    )

    status, body = call("POST", "/tools/create_work_order", {"asset_id": ASSET_ID})  # missing "problem"
    check("schema validation (missing required field)", status == 200 and body.get("status") == "error", str(body))

    passed = sum(1 for _, ok, _ in _results if ok)
    total = len(_results)
    print(f"\n{passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
