from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.models.order import Order
from app.schemas.order_schema import OrderCreate, OrderUpdate

def get_order(db: Session, order_id: str):
    """
    Get an order by ID
    """
    return db.query(Order).filter(Order.id == order_id).first()

def get_all_orders(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    priority: Optional[int] = None
):
    """
    Get all orders with optional filters
    """
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    if priority:
        query = query.filter(Order.priority == priority)
    
    return query.offset(skip).limit(limit).all()

def create_order(db: Session, order: OrderCreate):
    """
    Create a new order
    """
    order_dict = order.dict()

    # Remove order_id if it exists since the model uses id as primary key
    order_dict.pop("order_id", None)

    db_order = Order(**order_dict)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(db: Session, order_id: str, order: OrderUpdate):
    """
    Update an existing order
    """
    db_order = get_order(db, order_id=order_id)
    
    # Update order fields
    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: str):
    """
    Delete an order
    """
    db_order = get_order(db, order_id=order_id)
    db.delete(db_order)
    db.commit()
    return db_order
