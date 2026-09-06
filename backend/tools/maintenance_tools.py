from database import SessionLocal
from models import MaintenanceRecord
from tools.asset_tools import get_asset_details


def get_maintenance_history(asset_id: str) -> dict:
    get_asset_details(asset_id)  # raises ValueError if unknown

    db = SessionLocal()
    try:
        records = (
            db.query(MaintenanceRecord)
            .filter(MaintenanceRecord.asset_id == asset_id)
            .order_by(MaintenanceRecord.date.desc())
            .all()
        )
        return {
            "asset_id": asset_id,
            "records": [
                {"date": r.date, "description": r.description, "technician": r.technician} for r in records
            ],
        }
    finally:
        db.close()
