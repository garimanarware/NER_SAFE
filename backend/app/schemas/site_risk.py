from typing import Optional

from pydantic import BaseModel


class TerrainLayer(BaseModel):
    elevation_m: Optional[float] = None
    slope_deg: Optional[float] = None
    aspect_deg: Optional[float] = None


class WeatherLayer(BaseModel):
    rainfall_24h_mm: Optional[float] = None
    rainfall_7d_mm: Optional[float] = None


class GroundLayer(BaseModel):
    soil_moisture_pct: Optional[float] = None
    ground_movement_mm: Optional[float] = None


class HistoricalLayer(BaseModel):
    historical_events: int = 0


class SiteRiskResponse(BaseModel):
    location_id: str
    location_name: str
    district: str
    state: str

    latitude: float
    longitude: float

    risk_index: Optional[float] = None
    risk_level: str = "unassessed"
    confidence: Optional[float] = None

    terrain: TerrainLayer
    weather: WeatherLayer
    ground: GroundLayer
    historical: HistoricalLayer