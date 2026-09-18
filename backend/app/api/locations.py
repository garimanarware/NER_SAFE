from fastapi import APIRouter

from backend.app.database import locations_db
from backend.app.schemas.location import LocationCreate, LocationResponse


router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)

locations = locations_db


@router.post("/", response_model=LocationResponse)
@router.post("", response_model=LocationResponse, include_in_schema=False)
def create_location(location: LocationCreate):
    new_location = location.model_dump()

    locations_db.append(new_location)

    return new_location


@router.get("/", response_model=list[LocationResponse])
@router.get("", response_model=list[LocationResponse], include_in_schema=False)
def get_locations():
    return locations_db