from database import SessionLocal
from models import Asset


def get_asset_details(asset_id: str) -> dict:
    db = SessionLocal()
    try:
        asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
        if asset is None:
            raise ValueError(f"unknown asset_id: {asset_id}")
        return {
            "asset_id": asset.asset_id,
            "model": asset.model,
            "site_id": asset.site_id,
            "manufacturer": asset.manufacturer,
        }
    finally:
        db.close()
