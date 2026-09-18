from typing import Dict, Optional
from urllib.parse import urlencode
from urllib.request import urlopen
import json
import math


OPEN_METEO_ELEVATION_URL = (
    "https://api.open-meteo.com/v1/elevation"
)


def _get_elevations(
    coordinates: list[tuple[float, float]]
) -> list[Optional[float]]:
    """
    Retrieve DEM elevations for multiple coordinates.

    Open-Meteo Elevation API uses the Copernicus
    DEM GLO-90 (90 m resolution).
    """

    latitudes = ",".join(
        str(round(lat, 6))
        for lat, _ in coordinates
    )

    longitudes = ",".join(
        str(round(lon, 6))
        for _, lon in coordinates
    )

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
    }

    url = (
        OPEN_METEO_ELEVATION_URL
        + "?"
        + urlencode(params)
    )

    with urlopen(url, timeout=10) as response:
        data = json.loads(
            response.read().decode("utf-8")
        )

    elevations = data.get("elevation", [])

    return [
        float(value) if value is not None else None
        for value in elevations
    ]


def _calculate_slope_aspect(
    elevations: list[Optional[float]],
    latitude: float,
    longitude: float,
    spacing_m: float = 90.0,
) -> tuple[Optional[float], Optional[float]]:
    """
    Calculate slope and aspect from a 3x3 DEM neighborhood.

    Elevations are expected in this order:

        0 1 2
        3 4 5
        6 7 8

    Uses a Horn-style 3x3 terrain derivative.
    """

    if len(elevations) != 9:
        return None, None

    if any(value is None for value in elevations):
        return None, None

    z = [float(value) for value in elevations]

    dz_dx = (
        (z[2] + 2 * z[5] + z[8])
        - (z[0] + 2 * z[3] + z[6])
    ) / (8 * spacing_m)

    dz_dy = (
        (z[6] + 2 * z[7] + z[8])
        - (z[0] + 2 * z[1] + z[2])
    ) / (8 * spacing_m)

    slope_rad = math.atan(
        math.sqrt(
            dz_dx ** 2
            + dz_dy ** 2
        )
    )

    slope_deg = math.degrees(
        slope_rad
    )

    # Aspect measured clockwise from north.
    aspect_deg = (
        math.degrees(
            math.atan2(
                dz_dx,
                -dz_dy
            )
        )
        + 360
    ) % 360

    return (
        round(slope_deg, 2),
        round(aspect_deg, 2),
    )


def get_terrain_features(
    latitude: float,
    longitude: float
) -> Dict[str, Optional[float]]:
    """
    Retrieve real DEM terrain features for a coordinate.

    Source:
        Copernicus DEM GLO-90 via Open-Meteo Elevation API.

    Returns:
        elevation_m
        slope_deg
        aspect_deg

    Slope and aspect are derived from the surrounding
    3x3 DEM elevation neighborhood.
    """

    try:

        # Approximately one DEM cell around the target.
        # Latitude spacing is approximately 90 m.
        lat_offset = 0.00081

        # Longitude spacing depends on latitude.
        lon_offset = (
            0.00081
            / max(
                math.cos(
                    math.radians(latitude)
                ),
                0.1
            )
        )

        coordinates = [

            # North row
            (
                latitude + lat_offset,
                longitude - lon_offset
            ),
            (
                latitude + lat_offset,
                longitude
            ),
            (
                latitude + lat_offset,
                longitude + lon_offset
            ),

            # Middle row
            (
                latitude,
                longitude - lon_offset
            ),
            (
                latitude,
                longitude
            ),
            (
                latitude,
                longitude + lon_offset
            ),

            # South row
            (
                latitude - lat_offset,
                longitude - lon_offset
            ),
            (
                latitude - lat_offset,
                longitude
            ),
            (
                latitude - lat_offset,
                longitude + lon_offset
            ),
        ]

        elevations = _get_elevations(
            coordinates
        )

        center_elevation = elevations[4]

        slope_deg, aspect_deg = (
            _calculate_slope_aspect(
                elevations=elevations,
                latitude=latitude,
                longitude=longitude,
            )
        )

        return {
            "elevation_m": (
                round(center_elevation, 2)
                if center_elevation is not None
                else None
            ),

            "slope_deg": slope_deg,

            "aspect_deg": aspect_deg,
        }

    except Exception as exc:
        print(f"DEM terrain API error: {type(exc).__name__}: {exc}")
        raise

        return {
            "elevation_m": None,
            "slope_deg": None,
            "aspect_deg": None,
        }