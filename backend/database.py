import json
import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fieldsense.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

SEED_DATA_PATH = Path(__file__).parent / "data" / "seed_data.json"


def init_db() -> None:
    import models  # noqa: F401 (registers models on Base before create_all)

    Base.metadata.create_all(bind=engine)
    _seed_if_empty()


def check_connection() -> bool:
    """Used by /health for the M7 degraded-state UI requirement."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def _seed_if_empty() -> None:
    from models import Asset, MaintenanceRecord, PartsInventory

    db = SessionLocal()
    try:
        if db.query(Asset).count() > 0:
            return
        seed = json.loads(SEED_DATA_PATH.read_text())
        for asset in seed.get("assets", []):
            db.add(Asset(**asset))
        for record in seed.get("maintenance_records", []):
            db.add(MaintenanceRecord(**record))
        for part in seed.get("parts_inventory", []):
            db.add(PartsInventory(**part))
        db.commit()
    finally:
        db.close()
