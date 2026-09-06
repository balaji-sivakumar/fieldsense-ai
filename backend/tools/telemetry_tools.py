from tools.asset_tools import get_asset_details

# Deterministic baseline reading for the M1 vertical slice.
# Scenario-specific values (overheating, vibration, low pressure)
# are added by the telemetry simulator in M5.
_BASELINE_READING = {
    "temperature_f": 185.0,
    "vibration_mm_s": 2.1,
    "discharge_pressure_psi": 118.0,
}


def get_live_telemetry(asset_id: str) -> dict:
    get_asset_details(asset_id)  # raises ValueError if unknown
    return {"asset_id": asset_id, **_BASELINE_READING}
