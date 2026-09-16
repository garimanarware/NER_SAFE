from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ForecastCreate(BaseModel):
    location_id: str
    risk_level: str = "moderate"
    probability: float = Field(default=0.65, ge=0.0, le=1.0)
    forecast_time: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    explanation: Optional[str] = None


class ForecastResponse(BaseModel):
    forecast_id: str
    location_id: str
    risk_level: str
    probability: float
    forecast_time: datetime
    valid_until: datetime
    explanation: Optional[str] = None