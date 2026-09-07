import asyncio

from tool_registry import dispatch
from voice_ws import should_apply_risk_tier, should_flush_tool_results


def run(tool_name: str, args: dict, session_id: str = "test"):
    return asyncio.run(dispatch(tool_name, args, session_id))


def test_set_risk_level_valid():
    result = run("set_risk_level", {"level": "specialist_required", "reason": "vibration beyond safe limit"})
    assert result["status"] == "ok"
    assert result["result"]["risk_tier"] == "specialist_required"


def test_set_risk_level_invalid():
    result = run("set_risk_level", {"level": "on_fire", "reason": "x"})
    assert result["status"] == "error"


def test_escalate_to_specialist_returns_structured_handover():
    session_id = "handover-test-session"
    # Build up some session history the handover should be able to cite.
    run("get_live_telemetry", {"asset_id": "AC-104"}, session_id)
    run("search_manual", {"asset_model": "ACX-200", "fault_code": "E27"}, session_id)

    result = run(
        "escalate_to_specialist",
        {"asset_id": "AC-104", "reason": "vibration beyond safe limit"},
        session_id,
    )
    assert result["status"] == "ok"
    body = result["result"]
    assert body["risk_tier"] == "specialist_required"

    handover = body["handover"]
    assert handover["asset"]["model"] == "ACX-200"
    assert "temperature_f" in handover["current_telemetry"]
    assert isinstance(handover["maintenance_history"], list)
    assert len(handover["actions_already_taken"]) >= 2
    assert any(a["tool_name"] == "search_manual" for a in handover["actions_already_taken"])
    assert len(handover["manual_sources"]) >= 1
    assert handover["manual_sources"][0]["section"]


def test_escalate_to_specialist_unknown_asset_still_errors():
    result = run("escalate_to_specialist", {"asset_id": "AC-999", "reason": "x"}, "test")
    assert result["status"] == "error"


def test_should_flush_tool_results_on_normal_completion():
    assert should_flush_tool_results({"type": "reply.done", "status": "completed"}) is True


def test_should_flush_tool_results_discards_on_interruption():
    assert should_flush_tool_results({"type": "reply.done", "status": "interrupted"}) is False


def test_should_flush_tool_results_ignores_other_events():
    assert should_flush_tool_results({"type": "reply.started"}) is False


def test_explicit_set_risk_level_always_applies_including_downgrade():
    assert should_apply_risk_tier("set_risk_level", "observation", "dangerous_condition") is True


def test_escalate_to_specialist_cannot_downgrade_a_more_severe_tier():
    # This is the exact bug found in live testing: the agent classified
    # dangerous_condition, then called escalate_to_specialist (which tags
    # "specialist_required") — that must not silently downgrade the tier.
    assert should_apply_risk_tier("escalate_to_specialist", "specialist_required", "dangerous_condition") is False


def test_escalate_to_specialist_can_raise_the_tier():
    assert should_apply_risk_tier("escalate_to_specialist", "specialist_required", "observation") is True
