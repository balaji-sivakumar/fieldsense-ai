import asyncio

from tool_registry import dispatch


def run(tool_name: str, args: dict, session_id: str = "test"):
    return asyncio.run(dispatch(tool_name, args, session_id))


def test_get_asset_details_known_asset():
    result = run("get_asset_details", {"asset_id": "AC-104"})
    assert result["status"] == "ok"
    assert result["result"]["model"] == "ACX-200"


def test_get_asset_details_unknown_asset():
    result = run("get_asset_details", {"asset_id": "AC-999"})
    assert result["status"] == "error"
    assert "AC-999" in result["error"]


def test_get_live_telemetry_shape():
    result = run("get_live_telemetry", {"asset_id": "AC-104"})
    assert result["status"] == "ok"
    reading = result["result"]
    assert reading["asset_id"] == "AC-104"
    assert {"temperature_f", "vibration_mm_s", "discharge_pressure_psi"} <= reading.keys()


def test_get_live_telemetry_unknown_asset():
    result = run("get_live_telemetry", {"asset_id": "AC-999"})
    assert result["status"] == "error"


def test_search_manual_returns_stub_with_model():
    result = run("search_manual", {"asset_model": "ACX-200", "fault_code": "E27"})
    assert result["status"] == "ok"
    assert result["result"]["asset_model"] == "ACX-200"
    assert result["result"]["section"] == "Fault E27"


def test_get_maintenance_history_known_asset():
    result = run("get_maintenance_history", {"asset_id": "AC-104"})
    assert result["status"] == "ok"
    assert len(result["result"]["records"]) == 2


def test_get_maintenance_history_unknown_asset():
    result = run("get_maintenance_history", {"asset_id": "AC-999"})
    assert result["status"] == "error"


def test_check_parts_inventory_found():
    result = run("check_parts_inventory", {"site_id": "SITE-01", "part_number": "FLT-200"})
    assert result["status"] == "ok"
    assert result["result"]["found"] is True
    assert result["result"]["quantity_on_hand"] == 4


def test_check_parts_inventory_not_found():
    result = run("check_parts_inventory", {"site_id": "SITE-01", "part_number": "NOPE-000"})
    assert result["status"] == "ok"
    assert result["result"]["found"] is False


def test_create_work_order_persists():
    result = run(
        "create_work_order",
        {"asset_id": "AC-104", "problem": "will not start", "priority": "high"},
    )
    assert result["status"] == "ok"
    work_order = result["result"]
    assert work_order["work_order_id"] is not None
    assert work_order["status"] == "open"
    assert work_order["priority"] == "high"


def test_create_work_order_unknown_asset():
    result = run("create_work_order", {"asset_id": "AC-999", "problem": "x"})
    assert result["status"] == "error"


def test_record_observation_and_complete_work_order():
    created = run("create_work_order", {"asset_id": "AC-104", "problem": "overheating"})
    work_order_id = created["result"]["work_order_id"]

    observed = run(
        "record_observation",
        {"work_order_id": work_order_id, "measurement": "motor_temperature", "value": 105.0, "unit": "F"},
    )
    assert observed["status"] == "ok"
    assert observed["result"]["recorded"]["value"] == 105.0

    completed = run("complete_work_order", {"work_order_id": work_order_id, "resolution": "replaced filter"})
    assert completed["status"] == "ok"
    assert completed["result"]["status"] == "completed"


def test_record_observation_unknown_work_order():
    result = run(
        "record_observation",
        {"work_order_id": 999999, "measurement": "x", "value": 1.0, "unit": "F"},
    )
    assert result["status"] == "error"


def test_escalate_to_specialist():
    created = run("create_work_order", {"asset_id": "AC-104", "problem": "dangerous vibration"})
    work_order_id = created["result"]["work_order_id"]

    result = run(
        "escalate_to_specialist",
        {"asset_id": "AC-104", "reason": "vibration beyond safe limit", "work_order_id": work_order_id},
    )
    assert result["status"] == "ok"
    assert result["result"]["escalated"] is True


def test_escalate_to_specialist_unknown_asset():
    result = run("escalate_to_specialist", {"asset_id": "AC-999", "reason": "x"})
    assert result["status"] == "error"


def test_dispatch_unknown_tool():
    result = run("delete_everything", {})
    assert result["status"] == "error"
    assert "unknown tool" in result["error"]


def test_dispatch_missing_required_argument():
    result = run("create_work_order", {"asset_id": "AC-104"})  # missing "problem"
    assert result["status"] == "error"
    assert "invalid arguments" in result["error"]


def test_dispatch_wrong_argument_type():
    result = run("get_asset_details", {"asset_id": 104})  # should be a string
    assert result["status"] == "error"
    assert "invalid arguments" in result["error"]
