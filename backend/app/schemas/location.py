from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    location_id: str = Field(
        ...,
        description="Unique location identifier"
    )

    name: str = Field(
        ...,
        description="Village, town, or monitoring area name"
    )

    district: str = Field(
        ...,
        description="District name"
    )

    state: str = Field(
        ...,
        description="State name"
    )

    latitude: float = Field(
        ...,
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180
    )

    grid_id: str = Field(
        ...,
        description="Unique geospatial grid identifier"
    )


class LocationResponse(LocationCreate):
    pass