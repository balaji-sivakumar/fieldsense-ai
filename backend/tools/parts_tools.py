from database import SessionLocal
from models import PartsInventory


def check_parts_inventory(site_id: str, part_number: str) -> dict:
    db = SessionLocal()
    try:
        part = (
            db.query(PartsInventory)
            .filter(PartsInventory.site_id == site_id, PartsInventory.part_number == part_number)
            .first()
        )
        if part is None:
            return {"site_id": site_id, "part_number": part_number, "found": False, "quantity_on_hand": 0}
        return {
            "site_id": site_id,
            "part_number": part_number,
            "found": True,
            "description": part.description,
            "quantity_on_hand": part.quantity_on_hand,
        }
    finally:
        db.close()
