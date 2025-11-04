from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cost_parameters import CostParameter

def get_all_cost_parameters(db: Session) -> List[CostParameter]:
    """
    Get all cost parameters from database
    """
    return db.query(CostParameter).all()

def get_cost_parameters_by_commodity(db: Session, commodity: str) -> List[CostParameter]:
    """
    Get cost parameters for a specific commodity
    """
    return db.query(CostParameter).filter(CostParameter.commodity == commodity).all()

def get_cost_parameters_by_priority(db: Session, commodity: str, priority: str) -> Optional[CostParameter]:
    """
    Get cost parameters for a specific commodity and priority
    """
    return db.query(CostParameter).filter(
        CostParameter.commodity == commodity,
        CostParameter.priority == priority
    ).first()
