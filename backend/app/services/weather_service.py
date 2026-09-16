from typing import Dict, Optional
from urllib.parse import urlencode
from urllib.request import urlopen
import json


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_features(
    latitude: float,
    longitude: float
) -> Dict[str, Optional[float]]:

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "precipitation,"
            "soil_moisture_0_to_1cm,"
            "soil_moisture_1_to_3cm,"
            "soil_moisture_3_to_9cm,"
            "soil_moisture_9_to_27cm"
        ),
        "past_days": 7,
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    }

    url = OPEN_METEO_URL + "?" + urlencode(params)

    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

        hourly = data.get("hourly", {})

        precipitation = hourly.get(
            "precipitation", []
        )

        values = [
            float(v)
            for v in precipitation
            if v is not None
        ]

        rainfall_24h = sum(values[-24:])
        rainfall_7d = sum(values)

        moisture_layers = [
            hourly.get("soil_moisture_0_to_1cm", []),
            hourly.get("soil_moisture_1_to_3cm", []),
            hourly.get("soil_moisture_3_to_9cm", []),
            hourly.get("soil_moisture_9_to_27cm", []),
        ]

        latest_values = []

        for layer in moisture_layers:
            if layer and layer[-1] is not None:
                latest_values.append(
                    float(layer[-1])
                )

        if latest_values:
            soil_moisture_pct = (
                sum(latest_values)
                / len(latest_values)
            ) * 100
        else:
            soil_moisture_pct = None

        return {
            "rainfall_24h_mm": round(
                rainfall_24h, 2
            ),
            "rainfall_7d_mm": round(
                rainfall_7d, 2
            ),
            "soil_moisture_pct": (
                round(soil_moisture_pct, 2)
                if soil_moisture_pct is not None
                else None
            ),
        }

    except Exception as exc:
        print(
            f"Open-Meteo API error: {exc}"
        )

        return {
            "rainfall_24h_mm": None,
            "rainfall_7d_mm": None,
            "soil_moisture_pct": None,
        }