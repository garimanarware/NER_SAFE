from datetime import datetime, timezone, timedelta
from uuid import uuid4

from fastapi import APIRouter

from backend.app.database import forecasts_db
from backend.app.schemas.forecast import ForecastCreate, ForecastResponse


router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


@router.post("/", response_model=ForecastResponse)
def create_forecast(forecast: ForecastCreate):
    forecast_data = forecast.model_dump()

    if forecast_data.get("forecast_id") is None:
        forecast_data["forecast_id"] = str(uuid4())

    if forecast_data.get("valid_until") is None:
        forecast_data["valid_until"] = (
            datetime.now(timezone.utc) + timedelta(hours=6)
        )

    new_forecast = {
        **forecast_data
    }

    forecasts_db.append(new_forecast)

    return new_forecast


@router.get("/", response_model=list[ForecastResponse])
def get_forecasts():
    return forecasts_db