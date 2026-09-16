from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertCreate(BaseModel):
    location_id: str
    alert_type: str = "landslide_risk"
    severity: str = "moderate"
    message: str
    created_at: Optional[datetime] = None
    is_active: bool = True


class AlertResponse(BaseModel):
    alert_id: str
    location_id: str
    alert_type: str
    severity: str
    message: str
    created_at: datetime
    is_active: bool