from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String(100), nullable=False)
    customer_id = Column(Integer, nullable=True)
    material = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)  # Quantity in tons
    unit = Column(String(20), default="tons")
    status = Column(String(50), default="pending")  # pending, in_progress, completed
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    origin_plant = Column(String(100), nullable=False, default="Plant A")
    destination = Column(String(100), nullable=False)
    rate_per_ton = Column(Float, nullable=True)

    # For production tracking
    preferred_dispatch_date = Column(String, nullable=True)
    latest_delivery_date = Column(String, nullable=True)

    # Link to rake assigned to this order
    rake_id = Column(Integer, ForeignKey("rakes.id"), nullable=True)
    rake = relationship("Rake", back_populates="orders")

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
