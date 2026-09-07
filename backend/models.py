from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(String, primary_key=True)
    model = Column(String, nullable=False)
    site_id = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String, nullable=False)
    problem = Column(String, nullable=False)
    priority = Column(String, nullable=False, default="normal")
    status = Column(String, nullable=False, default="open")
    resolution = Column(String, nullable=True)


class WorkOrderEvent(Base):
    __tablename__ = "work_order_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    work_order_id = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)  # observation | completed | escalated
    detail = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String, nullable=False)
    date = Column(String, nullable=False)
    description = Column(String, nullable=False)
    technician = Column(String, nullable=False)


class PartsInventory(Base):
    __tablename__ = "parts_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(String, nullable=False)
    part_number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    quantity_on_hand = Column(Integer, nullable=False)


class ToolAuditLog(Base):
    __tablename__ = "tool_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tool_name = Column(String, nullable=False)
    args_json = Column(String, nullable=False)
    status = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # Full {"status":..., "result"|"error":...} dispatch() return value, so a
    # specialist handover (M6) can cite prior tool results (e.g. manual
    # sources) instead of re-querying or guessing. Nullable so a failed
    # write here never breaks a tool call.
    result_json = Column(String, nullable=True)
