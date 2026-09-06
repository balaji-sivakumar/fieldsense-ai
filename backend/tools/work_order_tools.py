from database import SessionLocal
from models import WorkOrder
from tools.asset_tools import get_asset_details


def create_work_order(asset_id: str, problem: str, priority: str = "normal") -> dict:
    get_asset_details(asset_id)  # raises ValueError if unknown

    db = SessionLocal()
    try:
        work_order = WorkOrder(asset_id=asset_id, problem=problem, priority=priority, status="open")
        db.add(work_order)
        db.commit()
        db.refresh(work_order)
        return {
            "work_order_id": work_order.id,
            "asset_id": work_order.asset_id,
            "problem": work_order.problem,
            "priority": work_order.priority,
            "status": work_order.status,
        }
    finally:
        db.close()
