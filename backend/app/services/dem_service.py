from typing import Dict, Optional


def get_terrain_features(
    latitude: float,
    longitude: float
) -> Dict[str, Optional[float]]:
    """
    Return terrain features for a geographic coordinate.

    DEM integration will populate these values from real
    elevation data. No terrain values are fabricated here.
    """

    return {
        "elevation_m": None,
        "slope_deg": None,
        "aspect_deg": None,
    }