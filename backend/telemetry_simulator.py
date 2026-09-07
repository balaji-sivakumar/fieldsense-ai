"""Deterministic per-asset telemetry scenarios for the M5 demo scenarios.

In-memory, global per asset_id (not per voice session) — represents
the simulated ground-truth state of the equipment, same as a real
panel reading, which any tool call or REST request should see
consistently regardless of which session asks. The demo operator sets
the active scenario before a conversation starts; the agent then
discovers it naturally through get_live_telemetry during the call.
"""

DEFAULT_SCENARIO = "normal"

SCENARIOS = {
    "normal": {
        "temperature_f": 185.0,
        "vibration_mm_s": 2.1,
        "discharge_pressure_psi": 118.0,
    },
    "overheating": {
        "temperature_f": 215.0,
        "vibration_mm_s": 2.3,
        "discharge_pressure_psi": 120.0,
    },
    "dangerous_vibration": {
        "temperature_f": 188.0,
        "vibration_mm_s": 5.2,
        "discharge_pressure_psi": 119.0,
    },
    "low_pressure": {
        "temperature_f": 182.0,
        "vibration_mm_s": 2.0,
        "discharge_pressure_psi": 88.0,
    },
}

_active_scenario: dict[str, str] = {}


def set_scenario(asset_id: str, scenario: str) -> None:
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario} (choices: {sorted(SCENARIOS)})")
    _active_scenario[asset_id] = scenario


def get_scenario(asset_id: str) -> str:
    return _active_scenario.get(asset_id, DEFAULT_SCENARIO)


def get_reading(asset_id: str) -> dict:
    return dict(SCENARIOS[get_scenario(asset_id)])
