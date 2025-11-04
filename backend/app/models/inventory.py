from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.core.database import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plant_location = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    material_grade = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, default="tons")
    storage_location = Column(String, nullable=False)
    production_schedule_date = Column(String)  # Will be updated daily
    next_production_date = Column(DateTime, nullable=True)
    production_rate = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class Inventory(Base):
    __tablename__ = "stockyards"

    stockyard_id = Column(String, primary_key=True, index=True)
    material = Column(String)
    capacity = Column(Float)
    location = Column(String)  # Latitude-Longitude as string, e.g., "23.6345,86.1432"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
