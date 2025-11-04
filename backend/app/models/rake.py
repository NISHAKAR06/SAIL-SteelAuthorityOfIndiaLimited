from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Rake(Base):
    __tablename__ = "rakes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rake_number = Column(String(50), nullable=False, unique=True)
    origin_plant = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    status = Column(String(50), default="Available")  # Available, In Transit, Loading, Maintenance
    capacity_tons = Column(Float, nullable=False, default=0.0)  # Capacity in tons
    total_wagons = Column(Integer, nullable=False, default=0)
    priority = Column(String(20), default="normal")  # low, normal, high
    current_location = Column(String(100), nullable=True)

    # For display/tracking dates
    departure_date = Column(String, nullable=True)
    expected_arrival_date = Column(String, nullable=True)
    last_maintenance_date = Column(String, nullable=True)

    # For live simulation
    transit_progress = Column(Float, default=0.0)  # Progress percentage 0-100
    departure_time = Column(DateTime, nullable=True)
    eta = Column(DateTime, nullable=True)  # Estimated time of arrival
    arrival_time = Column(DateTime, nullable=True)
    freight_type = Column(String(100), nullable=True)
    weight = Column(Float, nullable=True)  # Weight in tons

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    orders = relationship("Order", back_populates="rake")
