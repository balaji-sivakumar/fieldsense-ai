from tool_registry import dispatch


def test_get_asset_details_known_asset():
    result = dispatch("get_asset_details", {"asset_id": "AC-104"})
    assert result["status"] == "ok"
    assert result["result"]["model"] == "ACX-200"


def test_get_asset_details_unknown_asset():
    result = dispatch("get_asset_details", {"asset_id": "AC-999"})
    assert result["status"] == "error"
    assert "AC-999" in result["error"]


def test_get_live_telemetry_shape():
    result = dispatch("get_live_telemetry", {"asset_id": "AC-104"})
    assert result["status"] == "ok"
    reading = result["result"]
    assert reading["asset_id"] == "AC-104"
    assert {"temperature_f", "vibration_mm_s", "discharge_pressure_psi"} <= reading.keys()


def test_get_live_telemetry_unknown_asset():
    result = dispatch("get_live_telemetry", {"asset_id": "AC-999"})
    assert result["status"] == "error"


def test_search_manual_returns_stub_with_model():
    result = dispatch("search_manual", {"asset_model": "ACX-200", "fault_code": "E27"})
    assert result["status"] == "ok"
    assert result["result"]["asset_model"] == "ACX-200"
    assert result["result"]["section"] == "Fault E27"


def test_create_work_order_persists():
    result = dispatch(
        "create_work_order",
        {"asset_id": "AC-104", "problem": "will not start", "priority": "high"},
    )
    assert result["status"] == "ok"
    work_order = result["result"]
    assert work_order["work_order_id"] is not None
    assert work_order["status"] == "open"
    assert work_order["priority"] == "high"


def test_create_work_order_unknown_asset():
    result = dispatch("create_work_order", {"asset_id": "AC-999", "problem": "x"})
    assert result["status"] == "error"


def test_dispatch_unknown_tool():
    result = dispatch("delete_everything", {})
    assert result["status"] == "error"
    assert "unknown tool" in result["error"]
