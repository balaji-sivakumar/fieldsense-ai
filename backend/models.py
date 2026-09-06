from sqlalchemy import Column, Integer, String

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
