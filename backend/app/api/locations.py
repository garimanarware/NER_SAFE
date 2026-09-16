from fastapi import APIRouter
from backend.app.schemas.location import LocationCreate, LocationResponse


router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


locations: list[LocationResponse] = []


@router.post("/", response_model=LocationResponse)
def create_location(location: LocationCreate):
    new_location = LocationResponse(**location.model_dump())

    locations.append(new_location)

    return new_location


@router.get("/", response_model=list[LocationResponse])
def get_locations():
    return locations