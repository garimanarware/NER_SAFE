from fastapi import APIRouter, HTTPException

from backend.app.database import locations_db
from backend.app.services.dem_service import get_terrain_features


router = APIRouter(
    prefix="/terrain",
    tags=["Terrain"]
)


@router.get("/{location_id}")
def get_terrain(location_id: str):

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

    terrain = get_terrain_features(
        latitude=location["latitude"],
        longitude=location["longitude"]
    )

    return {
        "location_id": location_id,
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        **terrain
    }