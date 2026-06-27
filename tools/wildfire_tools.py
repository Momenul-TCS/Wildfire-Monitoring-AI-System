
import numpy as np
import joblib
import pandas as pd
from pydantic_ai import Tool
from configs.settings import settings

# ── Load models once at module level ──────────────────────
_risk_model  = None
_plume_model = None
_metadata    = None

def _load_models():
    global _risk_model, _plume_model, _metadata
    if _risk_model is None:
        _risk_model  = joblib.load(
            f"{settings.MODEL_DIR}/{settings.RISK_MODEL_FILE}"
        )
        _plume_model = joblib.load(
            f"{settings.MODEL_DIR}/{settings.PLUME_MODEL_FILE}"
        )
        _metadata    = joblib.load(
            f"{settings.MODEL_DIR}/model_metadata.pkl"
        )

def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply same feature engineering used during training."""
    df = df.copy()
    df["heat_index"]   = df["temperature"] *                          (1 + (100 - df["humidity"]) / 100)
    df["wind_drought"] = df["wind_speed"] * df["drought_index"]
    df["fire_weather"] = (df["temperature"] / 50) *                          ((100 - df["humidity"]) / 100) *                          (df["wind_speed"] / 130)
    return df

# ── Tool 1: Predict Wildfire Risk ─────────────────────────
@Tool
def predict_wildfire_risk(
    temperature   : float,
    humidity      : float,
    wind_speed    : float,
    wind_direction: float,
    rainfall      : float,
    pressure      : float,
    drought_index : float
) -> dict:
    """
    Predict wildfire risk probability using the trained
    XGBoost model given current weather conditions.
    Returns probability (0-1), risk category, and
    recommended actions.
    Args:
        temperature: Temperature in Celsius
        humidity: Relative humidity percentage
        wind_speed: Wind speed in km/h
        wind_direction: Wind direction in degrees
        rainfall: Rainfall in mm
        pressure: Atmospheric pressure in hPa
        drought_index: Drought index (0-10)
    """
    _load_models()
    meta = _metadata

    df_input = pd.DataFrame([{
        "temperature"   : temperature,
        "humidity"      : humidity,
        "wind_speed"    : wind_speed,
        "wind_direction": wind_direction,
        "rainfall"      : rainfall,
        "pressure"      : pressure,
        "drought_index" : drought_index,
    }])

    df_input  = _engineer_features(df_input)
    risk_X    = df_input[meta["risk_features"]].values
    prob      = float(_risk_model.predict_proba(risk_X)[0][1])

    thresh = meta["risk_thresholds"]
    cat    = ("Critical" if prob >= thresh["critical"] else
              "High"     if prob >= thresh["high"]     else
              "Medium"   if prob >= thresh["medium"]   else "Low")

    actions = {
        "Critical": "IMMEDIATE evacuation. Alert all emergency services.",
        "High"    : "Prepare evacuation plans. Alert fire departments.",
        "Medium"  : "Monitor conditions. Firefighters on standby.",
        "Low"     : "No immediate action. Continue monitoring.",
    }

    return {
        "probability"       : round(prob, 4),
        "percentage"        : round(prob * 100, 1),
        "risk_category"     : cat,
        "recommended_action": actions[cat],
        "input_conditions"  : {
            "temperature"   : temperature,
            "humidity"      : humidity,
            "wind_speed"    : wind_speed,
            "drought_index" : drought_index,
        }
    }

# ── Tool 2: Estimate Fire Spread ──────────────────────────
@Tool
def estimate_fire_spread(
    wind_speed    : float,
    humidity      : float,
    temperature   : float,
    drought_index : float,
) -> dict:
    """
    Estimate wildfire spread radius and smoke plume
    expansion using the trained plume model.
    Returns spread_radius_km and impact zones.
    Args:
        wind_speed: Wind speed in km/h
        humidity: Relative humidity percentage
        temperature: Temperature in Celsius
        drought_index: Drought index (0-10)
    """
    _load_models()
    meta = _metadata

    df_input = pd.DataFrame([{
        "wind_speed"    : wind_speed,
        "humidity"      : humidity,
        "temperature"   : temperature,
        "drought_index" : drought_index,
    }])

    df_input  = _engineer_features(df_input)
    plume_X   = df_input[
        [f for f in meta["plume_features"] if f in df_input.columns]
    ].values

    spread = float(max(0.1, _plume_model.predict(plume_X)[0]))

    return {
        "spread_radius_km"  : round(spread, 2),
        "impact_zones"      : {
            "immediate_km"  : round(spread * 0.3, 2),
            "nearby_km"     : round(spread * 0.6, 2),
            "extended_km"   : round(spread,       2),
        },
        "estimated_area_km2": round(np.pi * spread ** 2, 2),
        "conditions"        : {
            "wind_speed"    : wind_speed,
            "humidity"      : humidity,
            "drought_index" : drought_index,
        }
    }

# ── Tool 3: Calculate Plume Direction ─────────────────────
@Tool
def calculate_plume_direction(
    wind_direction: float,
    spread_radius : float
) -> dict:
    """
    Calculate smoke plume expansion direction and
    affected coordinates based on wind direction.
    Returns cardinal direction and bearing info.
    Args:
        wind_direction: Wind direction in degrees (0-360)
        spread_radius: Fire spread radius in km
    """
    directions = [
        "N","NNE","NE","ENE","E","ESE","SE","SSE",
        "S","SSW","SW","WSW","W","WNW","NW","NNW"
    ]
    idx       = int((wind_direction + 11.25) / 22.5) % 16
    cardinal  = directions[idx]
    rad       = np.radians(wind_direction)

    return {
        "wind_direction_deg": round(wind_direction, 1),
        "cardinal_direction": cardinal,
        "plume_vector"      : {
            "dx_km": round(spread_radius * np.sin(rad), 3),
            "dy_km": round(spread_radius * np.cos(rad), 3),
        },
        "affected_bearing"  : f"Plume moving {cardinal} "
                               f"for {spread_radius:.1f} km",
    }
