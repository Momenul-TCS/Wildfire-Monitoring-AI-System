
import pandas as pd
import numpy as np
from datetime import datetime
from pydantic_ai import Tool
from typing import Optional
from configs.settings import settings

# ── Load weather dataset once at module level ─────────────
_weather_df = None

def _get_weather_df() -> pd.DataFrame:
    """Lazy load weather dataset."""
    global _weather_df
    if _weather_df is None:
        path = f"{settings.DATASET_DIR}/{settings.WEATHER_DATASET}"
        _weather_df = pd.read_csv(path, parse_dates=["timestamp"])
    return _weather_df

# ── Tool 1: Get Latest Weather ────────────────────────────
@Tool
def get_latest_weather(latitude: float, longitude: float) -> dict:
    """
    Get the latest weather reading for a given location in California.
    Returns temperature, humidity, wind speed, rainfall,
    pressure, drought index and timestamp.
    Args:
        latitude: Location latitude (32.5 to 42.0)
        longitude: Location longitude (-124.5 to -114.0)
    """
    df = _get_weather_df()

    # Find closest location using Manhattan distance
    df["dist"] = (
        (df["latitude"]  - latitude).abs() +
        (df["longitude"] - longitude).abs()
    )
    closest = df.nsmallest(10, "dist").sort_values(
        "timestamp", ascending=False
    ).iloc[0]

    return {
        "timestamp"      : str(closest["timestamp"]),
        "latitude"       : round(float(closest["latitude"]),  4),
        "longitude"      : round(float(closest["longitude"]), 4),
        "temperature"    : round(float(closest["temperature"]), 2),
        "humidity"       : round(float(closest["humidity"]),    2),
        "wind_speed"     : round(float(closest["wind_speed"]),  2),
        "wind_direction" : round(float(closest["wind_direction"]), 2),
        "rainfall"       : round(float(closest["rainfall"]),   2),
        "pressure"       : round(float(closest["pressure"]),   2),
        "drought_index"  : round(float(closest["drought_index"]), 2),
        "wildfire_occurred": int(closest["wildfire_occurred"]),
    }

# ── Tool 2: Get Weather Forecast ──────────────────────────
@Tool
def get_weather_forecast(
    latitude: float,
    longitude: float,
    days_ahead: int = 3
) -> dict:
    """
    Get a simulated weather forecast for a location
    for the next N days based on historical patterns.
    Args:
        latitude: Location latitude
        longitude: Location longitude
        days_ahead: Number of days to forecast (1-7)
    """
    df    = _get_weather_df()
    month = datetime.now().month

    # Filter by season (same month historically)
    seasonal = df[df["timestamp"].dt.month == month]
    if len(seasonal) < 10:
        seasonal = df

    # Closest location
    seasonal = seasonal.copy()
    seasonal["dist"] = (
        (seasonal["latitude"]  - latitude).abs() +
        (seasonal["longitude"] - longitude).abs()
    )
    nearby = seasonal.nsmallest(200, "dist")

    forecast = []
    for day in range(1, min(days_ahead, 7) + 1):
        sample = nearby.sample(1).iloc[0]
        # Add slight random variation
        forecast.append({
            "day"           : day,
            "temperature"   : round(float(sample["temperature"])
                                    + np.random.normal(0, 1.5), 1),
            "humidity"      : round(float(sample["humidity"])
                                    + np.random.normal(0, 3), 1),
            "wind_speed"    : round(max(0, float(sample["wind_speed"])
                                    + np.random.normal(0, 5)), 1),
            "rainfall"      : round(max(0, float(sample["rainfall"])
                                    + np.random.normal(0, 1)), 1),
            "drought_index" : round(float(sample["drought_index"]), 2),
        })

    return {
        "location"      : {"latitude": latitude, "longitude": longitude},
        "forecast_days" : days_ahead,
        "forecast"      : forecast,
    }

# ── Tool 3: Get Fire Risk Score ───────────────────────────
@Tool
def get_fire_weather_index(
    temperature: float,
    humidity: float,
    wind_speed: float,
    rainfall: float,
    drought_index: float
) -> dict:
    """
    Calculate a simplified Fire Weather Index (FWI)
    from current weather conditions.
    Returns fwi_score (0-100) and risk_level.
    Args:
        temperature: Current temperature in Celsius
        humidity: Relative humidity percentage
        wind_speed: Wind speed in km/h
        rainfall: Rainfall in mm
        drought_index: Drought index (0-10)
    """
    # Normalised component scores (0-1)
    temp_score    = np.clip((temperature - 20) / 30, 0, 1)
    hum_score     = np.clip((40 - humidity)    / 35, 0, 1)
    wind_score    = np.clip(wind_speed         / 100, 0, 1)
    rain_score    = np.clip((5 - rainfall)     / 5,  0, 1)
    drought_score = np.clip(drought_index      / 10, 0, 1)

    fwi = (
        0.30 * temp_score    +
        0.25 * hum_score     +
        0.20 * wind_score    +
        0.15 * rain_score    +
        0.10 * drought_score
    ) * 100

    fwi = round(float(fwi), 2)

    risk_level = (
        "Critical" if fwi >= 80 else
        "High"     if fwi >= 60 else
        "Medium"   if fwi >= 40 else "Low"
    )

    return {
        "fwi_score"    : fwi,
        "risk_level"   : risk_level,
        "components"   : {
            "temperature_score" : round(temp_score * 100, 1),
            "humidity_score"    : round(hum_score  * 100, 1),
            "wind_score"        : round(wind_score * 100, 1),
            "rain_score"        : round(rain_score * 100, 1),
            "drought_score"     : round(drought_score * 100, 1),
        }
    }
