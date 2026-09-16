from fastapi import APIRouter, HTTPException

from backend.app.database import locations_db
from backend.app.services.dem_service import get_terrain_features
from backend.app.services.weather_service import get_weather_features

from backend.app.schemas.site_risk import (
    SiteRiskResponse,
    TerrainLayer,
    WeatherLayer,
    GroundLayer,
    HistoricalLayer,
)


router = APIRouter(
    prefix="/site-risk",
    tags=["Site Risk"]
)


def calculate_risk(
    rainfall_24h: float | None,
    rainfall_7d: float | None,
    slope: float | None,
    soil_moisture: float | None,
    ground_movement: float | None,
) -> float:

    # Fallback values are ONLY used when an upstream
    # data source does not provide that signal.

    rainfall_24h = rainfall_24h if rainfall_24h is not None else 0
    rainfall_7d = rainfall_7d if rainfall_7d is not None else 0

    slope = slope if slope is not None else 28
    soil_moisture = soil_moisture if soil_moisture is not None else 50
    ground_movement = (
        ground_movement
        if ground_movement is not None
        else 0
    )

    rainfall_24h_score = min(
        (rainfall_24h / 100) * 100,
        100
    )

    rainfall_7d_score = min(
        (rainfall_7d / 300) * 100,
        100
    )

    slope_score = min(
        (slope / 45) * 100,
        100
    )

    soil_score = min(
        soil_moisture,
        100
    )

    movement_score = min(
        (ground_movement / 10) * 100,
        100
    )

    risk = (
        0.30 * rainfall_24h_score
        + 0.20 * rainfall_7d_score
        + 0.20 * slope_score
        + 0.20 * soil_score
        + 0.10 * movement_score
    )

    return round(
        min(max(risk, 0), 100),
        1
    )


def get_risk_level(risk_index: float) -> str:

    if risk_index >= 80:
        return "critical"

    if risk_index >= 60:
        return "high"

    if risk_index >= 35:
        return "moderate"

    return "low"


@router.get(
    "/{location_id}",
    response_model=SiteRiskResponse
)
def get_site_risk(location_id: str):

    location = next(
        (
            item
            for item in locations_db
            if item["location_id"] == location_id
        ),
        None
    )

    if location is None:
        raise HTTPException(
            status_code=404,
            detail=f"Location {location_id} not found"
        )

    latitude = location["latitude"]
    longitude = location["longitude"]

    # -----------------------------------------
    # LIVE TERRAIN DATA
    # -----------------------------------------

    terrain_data = get_terrain_features(
        latitude=latitude,
        longitude=longitude
    )

    # -----------------------------------------
    # LIVE WEATHER + SOIL DATA
    # -----------------------------------------

    weather_data = get_weather_features(
        latitude=latitude,
        longitude=longitude
    )

    # -----------------------------------------
    # CURRENT GROUND DATA
    # -----------------------------------------

    # Replace these when ESP32 sensors are connected.
    ground_movement = 4.2

    # Use live soil moisture from API.
    soil_moisture = weather_data[
        "soil_moisture_pct"
    ]

    # -----------------------------------------
    # HISTORICAL DATA
    # -----------------------------------------

    historical_events = 3

    # -----------------------------------------
    # RISK ENGINE
    # -----------------------------------------

    risk_index = calculate_risk(
        rainfall_24h=weather_data[
            "rainfall_24h_mm"
        ],
        rainfall_7d=weather_data[
            "rainfall_7d_mm"
        ],
        slope=terrain_data[
            "slope_deg"
        ],
        soil_moisture=soil_moisture,
        ground_movement=ground_movement,
    )

    risk_level = get_risk_level(
        risk_index
    )

    # Prototype confidence.
    # Later this should come from model/data quality.
    confidence = 0.82

    return SiteRiskResponse(

        location_id=location[
            "location_id"
        ],

        location_name=location.get(
            "name",
            "Unknown"
        ),

        district=location[
            "district"
        ],

        state=location[
            "state"
        ],

        latitude=latitude,

        longitude=longitude,

        risk_index=risk_index,

        risk_level=risk_level,

        confidence=confidence,

        terrain=TerrainLayer(
            elevation_m=terrain_data[
                "elevation_m"
            ],

            slope_deg=terrain_data[
                "slope_deg"
            ],

            aspect_deg=terrain_data[
                "aspect_deg"
            ],
        ),

        weather=WeatherLayer(
            rainfall_24h_mm=weather_data[
                "rainfall_24h_mm"
            ],

            rainfall_7d_mm=weather_data[
                "rainfall_7d_mm"
            ],
        ),

        ground=GroundLayer(
            soil_moisture_pct=soil_moisture,

            ground_movement_mm=ground_movement,
        ),

        historical=HistoricalLayer(
            historical_events=historical_events
        ),
    )