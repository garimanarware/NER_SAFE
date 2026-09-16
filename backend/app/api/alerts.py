from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter

from backend.app.database import alerts_db
from backend.app.schemas.alert import AlertCreate, AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/", response_model=AlertResponse)
def create_alert(alert: AlertCreate):
    new_alert = {
        "alert_id": str(uuid4()),
        **alert.model_dump(),
    }

    if new_alert["created_at"] is None:
        new_alert["created_at"] = datetime.now(timezone.utc)

    alerts_db.append(new_alert)
    return new_alert


@router.post("/generate/{location_id}", response_model=AlertResponse)
def generate_alert(location_id: str):
    new_alert = {
        "alert_id": str(uuid4()),
        "location_id": location_id,
        "alert_type": "landslide_risk",
        "severity": "moderate",
        "message": "Demonstration alert. Real sensor and ML data will be connected later.",
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }

    alerts_db.append(new_alert)
    return new_alert


@router.get("/", response_model=list[AlertResponse])
def get_alerts():
    return alerts_db


@router.get("/active", response_model=list[AlertResponse])
def get_active_alerts():
    return [
        alert for alert in alerts_db
        if alert.get("is_active") is True
    ]