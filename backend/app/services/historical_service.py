from pathlib import Path
from typing import Dict
import csv
import math


INVENTORY_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "ner_landslide_inventory.csv"
)


def _distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Calculate great-circle distance between two coordinates."""

    radius_km = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(dlon / 2) ** 2
    )

    return (
        radius_km
        * 2
        * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )
    )


_INVENTORY_CACHE: list[dict] | None = None


def _load_inventory() -> list[dict]:
    """Load the NER landslide inventory from the local CSV."""
    global _INVENTORY_CACHE
    if _INVENTORY_CACHE is not None:
        return _INVENTORY_CACHE

    if not INVENTORY_PATH.exists():
        raise FileNotFoundError(
            f"Historical inventory not found: {INVENTORY_PATH}"
        )

    records = []

    with INVENTORY_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                f"Historical inventory has no CSV header: {INVENTORY_PATH}"
            )

        # Normalize column names.
        reader.fieldnames = [
            field.strip().lower()
            if field is not None
            else ""
            for field in reader.fieldnames
        ]

        for row in reader:
            record = {}

            for key, value in row.items():
                if key is None:
                    continue

                clean_key = key.strip().lower()

                if value is None:
                    clean_value = ""
                else:
                    clean_value = value.strip()

                record[clean_key] = clean_value

            records.append(record)

    _INVENTORY_CACHE = records
    return records


def _get_float(
    record: dict,
    field: str,
) -> float | None:
    """Safely convert a CSV field to a float."""

    value = record.get(field)

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_historical_landslides(
    latitude: float,
    longitude: float,
    radius_km: float = 25.0,
) -> Dict[str, object]:
    """Search the NER landslide inventory around a location."""

    inventory = _load_inventory()

    nearby_events = []

    for record in inventory:

        event_lat = _get_float(record, "latitude")
        event_lon = _get_float(record, "longitude")

        # Skip records without usable coordinates.
        if event_lat is None or event_lon is None:
            continue

        # Skip invalid geographic coordinates.
        if not (-90 <= event_lat <= 90):
            continue

        if not (-180 <= event_lon <= 180):
            continue

        distance = _distance_km(
            latitude,
            longitude,
            event_lat,
            event_lon,
        )

        if distance <= radius_km:

            nearby_events.append(
                {
                    "sl_no": record.get("sl_no"),
                    "slide_no": record.get("slide_no"),
                    "state": record.get("state"),
                    "district": record.get("district"),
                    "slide_name": record.get("slide_name"),
                    "latitude": event_lat,
                    "longitude": event_lon,
                    "distance_km": round(distance, 2),
                    "description": record.get(
                        "description",
                        "",
                    ),
                    "material": record.get(
                        "material",
                        "",
                    ),
                    "movement": record.get(
                        "movement",
                        "",
                    ),
                    "history": record.get(
                        "history",
                        "",
                    ),
                }
            )

    nearby_events.sort(
        key=lambda item: item["distance_km"]
    )

    return {
        "historical_events": len(nearby_events),
        "nearby_events": nearby_events,
        "nearest_event_distance_km": (
            nearby_events[0]["distance_km"]
            if nearby_events
            else None
        ),
        "search_radius_km": radius_km,
        "source": "Uploaded NER landslide inventory",
    }