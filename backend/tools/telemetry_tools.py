from telemetry_simulator import get_reading
from tools.asset_tools import get_asset_details


def get_live_telemetry(asset_id: str) -> dict:
    get_asset_details(asset_id)  # raises ValueError if unknown
    return {"asset_id": asset_id, **get_reading(asset_id)}
