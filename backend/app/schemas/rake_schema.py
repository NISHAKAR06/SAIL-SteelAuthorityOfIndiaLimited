from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class RakeBase(BaseModel):
    rake_number: str = Field(..., description="Unique rake number")
    origin_plant: str = Field(..., description="Origin plant")
    destination: str = Field(..., description="Destination")
    status: str = Field("Available", description="Rake status")
    capacity_tons: float = Field(0.0, description="Capacity in tons")
    total_wagons: int = Field(0, description="Total number of wagons")
    priority: str = Field("normal", description="Priority level")
    current_location: Optional[str] = Field(None, description="Current location")
    departure_date: Optional[str] = Field(None, description="Departure date")
    expected_arrival_date: Optional[str] = Field(None, description="Expected arrival date")
    last_maintenance_date: Optional[str] = Field(None, description="Last maintenance date")
    transit_progress: float = Field(0.0, description="Transit progress percentage")
    departure_time: Optional[datetime] = Field(None, description="Departure time")
    eta: Optional[datetime] = Field(None, description="Estimated time of arrival")
    arrival_time: Optional[datetime] = Field(None, description="Arrival time")
    freight_type: Optional[str] = Field(None, description="Freight type")
    weight: Optional[float] = Field(None, description="Weight in tons")

class RakeCreate(RakeBase):
    pass

class RakeUpdate(BaseModel):
    rake_number: Optional[str] = None
    origin_plant: Optional[str] = None
    destination: Optional[str] = None
    status: Optional[str] = None
    capacity_tons: Optional[float] = None
    total_wagons: Optional[int] = None
    priority: Optional[str] = None
    current_location: Optional[str] = None
    departure_date: Optional[str] = None
    expected_arrival_date: Optional[str] = None
    last_maintenance_date: Optional[str] = None
    transit_progress: Optional[float] = None
    departure_time: Optional[datetime] = None
    eta: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    freight_type: Optional[str] = None
    weight: Optional[float] = None

class RakeInDB(RakeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class Rake(RakeInDB):
    pass
