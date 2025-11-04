from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.route_transport import RouteTransport

def get_all_route_transport(db: Session) -> List[RouteTransport]:
    """
    Get all route transport information from database
    """
    return db.query(RouteTransport).all()

def get_route_transport_by_origin_destination(db: Session, origin: str, destination: str) -> Optional[RouteTransport]:
    """
    Get route transport information for specific origin and destination
    """
    return db.query(RouteTransport).filter(
        RouteTransport.origin == origin,
        RouteTransport.destination == destination
    ).first()

def get_routes_by_origin(db: Session, origin: str) -> List[RouteTransport]:
    """
    Get all routes originating from a specific location
    """
    return db.query(RouteTransport).filter(RouteTransport.origin == origin).all()

def get_routes_by_destination(db: Session, destination: str) -> List[RouteTransport]:
    """
    Get all routes terminating at a specific destination
    """
    return db.query(RouteTransport).filter(RouteTransport.destination == destination).all()
