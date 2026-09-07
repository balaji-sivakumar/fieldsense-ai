import asyncio

import pytest

import telemetry_simulator
from tool_registry import dispatch


@pytest.fixture(autouse=True)
def reset_simulator():
    telemetry_simulator._active_scenario.clear()
    yield
    telemetry_simulator._active_scenario.clear()


def run(tool_name: str, args: dict):
    return asyncio.run(dispatch(tool_name, args, session_id="test"))


def test_defaults_to_normal():
    assert telemetry_simulator.get_scenario("AC-104") == "normal"
    result = run("get_live_telemetry", {"asset_id": "AC-104"})
    assert result["result"]["temperature_f"] == 185.0


def test_set_scenario_changes_reading():
    telemetry_simulator.set_scenario("AC-104", "overheating")
    result = run("get_live_telemetry", {"asset_id": "AC-104"})
    assert result["result"]["temperature_f"] == 215.0


def test_dangerous_vibration_scenario():
    telemetry_simulator.set_scenario("AC-104", "dangerous_vibration")
    result = run("get_live_telemetry", {"asset_id": "AC-104"})
    assert result["result"]["vibration_mm_s"] == 5.2


def test_low_pressure_scenario():
    telemetry_simulator.set_scenario("AC-104", "low_pressure")
    result = run("get_live_telemetry", {"asset_id": "AC-104"})
    assert result["result"]["discharge_pressure_psi"] == 88.0


def test_scenarios_are_per_asset():
    telemetry_simulator.set_scenario("AC-104", "overheating")
    assert telemetry_simulator.get_scenario("AC-105") == "normal"


def test_unknown_scenario_rejected():
    with pytest.raises(ValueError):
        telemetry_simulator.set_scenario("AC-104", "meltdown")
