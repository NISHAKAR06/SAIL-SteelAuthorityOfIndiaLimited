from sqlalchemy import Column, String, Float, Integer
from app.core.database import Base

class CostParameter(Base):
    __tablename__ = "cost_parameters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    commodity = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    cost_per_tonne_km = Column(Float, nullable=False)
    loading_cost_per_wagon = Column(Float, nullable=False)
    unloading_cost_per_wagon = Column(Float, nullable=False)
    penalty_per_day_delay = Column(Float, nullable=False)
    priority_multiplier = Column(Float, nullable=False)
    fuel_surcharge_per_wagon = Column(Float, nullable=False)
