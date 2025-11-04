from sqlalchemy import Column, String, Float, Integer
from app.core.database import Base

class RouteTransport(Base):
    __tablename__ = "route_transport_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    transit_time_days = Column(Integer, nullable=False)
    preferred_route = Column(String, nullable=False)
    alternate_route = Column(String, nullable=True)
    track_capacity_wagons_per_day = Column(Integer, nullable=False)
    route_constraints = Column(String, nullable=True)
    expected_delays_days = Column(Integer, nullable=True)
    railway_zone = Column(String, nullable=False)
