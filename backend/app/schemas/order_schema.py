from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class OrderBase(BaseModel):
    customer_name: str = Field(..., description="Customer name")
    customer_id: Optional[int] = Field(None, description="Customer ID")
    material: str = Field(..., description="Material type")
    quantity: float = Field(..., description="Quantity in tons")
    unit: str = Field("tons", description="Unit of measurement")
    status: str = Field("pending", description="Order status")
    priority: str = Field("normal", description="Order priority")
    origin_plant: str = Field("Plant A", description="Origin plant")
    destination: str = Field(..., description="Destination")
    rate_per_ton: Optional[float] = Field(None, description="Rate per ton")
    preferred_dispatch_date: Optional[str] = Field(None, description="Preferred dispatch date")
    latest_delivery_date: Optional[str] = Field(None, description="Latest delivery date")
    rake_id: Optional[int] = Field(None, description="Assigned rake ID")

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_id: Optional[int] = None
    material: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    origin_plant: Optional[str] = None
    destination: Optional[str] = None
    rate_per_ton: Optional[float] = None
    preferred_dispatch_date: Optional[str] = None
    latest_delivery_date: Optional[str] = None
    rake_id: Optional[int] = None

class OrderInDB(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class Order(OrderInDB):
    pass
