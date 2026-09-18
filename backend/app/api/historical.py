from collections import Counter
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.app.database import locations_db
from backend.app.services.historical_service import (
    get_historical_landslides,
    _load_inventory,
)

router = APIRouter(
    prefix="/historical",
    tags=["Historical Landslides"],
)


@router.get("/summary")
def get_inventory_summary():
    """Return regional summary statistics from the landslide inventory."""
    try:
        records = _load_inventory()
        state_counts = dict(
            Counter(
                r.get("state", "Unknown")
                for r in records
                if r.get("state")
            )
        )
        return {
            "total_records": len(records),
            "state_counts": state_counts,
            "source": "Uploaded NER landslide inventory (Geological Survey compilation)",
            "inventory_coverage": "North Eastern Region (7 States + Sikkim & Tripura)",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read landslide inventory: {exc}",
        )


@router.get("/records")
def get_inventory_records(
    state: Optional[str] = Query(None, description="Filter by state name"),
    limit: int = Query(50, ge=1, le=500, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """Retrieve paginated records from the local landslide inventory."""
    records = _load_inventory()
    if state:
        state_lower = state.strip().lower()
        records = [
            r for r in records
            if r.get("state", "").strip().lower() == state_lower
        ]

    total = len(records)
    sliced = records[offset : offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "records": sliced,
    }


@router.get("/{location_id}")
def get_location_historical(
    location_id: str,
    radius_km: float = Query(25.0, ge=1.0, le=100.0, description="Search radius in kilometers"),
):
    """Retrieve historical landslide inventory records within radius of a monitored location."""
    location = next(
        (item for item in locations_db if item["location_id"] == location_id),
        None,
    )

    if location is None:
        raise HTTPException(
            status_code=404,
            detail=f"Location {location_id} not found",
        )

    data = get_historical_landslides(
        latitude=location["latitude"],
        longitude=location["longitude"],
        radius_km=radius_km,
    )

    return {
        "location_id": location_id,
        "location_name": location.get("name", "Unknown"),
        "district": location.get("district", ""),
        "state": location.get("state", ""),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        **data,
    }
