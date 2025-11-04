from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.models.rake import Rake
from app.schemas.rake_schema import RakeCreate, RakeUpdate
from app.schemas.optimize_schema import OptimizationRequest, OptimizationResult
from app.ml.rake_optimizer import optimize_rakes

def get_rake(db: Session, rake_id: str):
    """
    Get a rake by ID
    """
    return db.query(Rake).filter(Rake.id == rake_id).first()

def get_all_rakes(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """
    Get all rakes with optional status filter
    """
    query = db.query(Rake)
    if status:
        query = query.filter(Rake.status == status)
    
    return query.offset(skip).limit(limit).all()

def create_rake(db: Session, rake: RakeCreate):
    """
    Create a new rake
    """
    db_rake = Rake(**rake.dict())
    db.add(db_rake)
    db.commit()
    db.refresh(db_rake)
    return db_rake

def update_rake(db: Session, rake_id: str, rake: RakeUpdate):
    """
    Update an existing rake
    """
    db_rake = get_rake(db, rake_id=rake_id)
    
    # Update rake fields
    for key, value in rake.dict().items():
        setattr(db_rake, key, value)
    
    db.commit()
    db.refresh(db_rake)
    return db_rake

def delete_rake(db: Session, rake_id: str):
    """
    Delete a rake
    """
    db_rake = get_rake(db, rake_id=rake_id)
    db.delete(db_rake)
    db.commit()
    return db_rake
