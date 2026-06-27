
import pandas as pd
import numpy as np
from pydantic_ai import Tool
from geopy.distance import geodesic
from configs.settings import settings

# ── Load infrastructure dataset once ──────────────────────
_infra_df = None

def _get_infra_df() -> pd.DataFrame:
    global _infra_df
    if _infra_df is None:
        path      = f"{settings.DATASET_DIR}/{settings.INFRA_DATASET}"
        _infra_df = pd.read_csv(path)
    return _infra_df

# ── Tool 1: Find Nearby Assets ────────────────────────────
@Tool
def find_nearby_assets(
    latitude      : float,
    longitude     : float,
    radius_km     : float = 5.0,
    asset_type    : str   = "all"
) -> dict:
    """
    Find infrastructure assets within a given radius
    of a location. Returns counts and details of
    nearby houses, hospitals, schools, transformers,
    power lines, shelters and emergency centers.
    Args:
        latitude: Center point latitude
        longitude: Center point longitude
        radius_km: Search radius in kilometers
        asset_type: Filter by type or "all"
    """
    df     = _get_infra_df().copy()
    origin = (latitude, longitude)

    # Filter by type if specified
    if asset_type != "all":
        df = df[df["asset_type"] == asset_type]

    # Compute distances
    df["distance_km"] = df.apply(
        lambda row: round(
            geodesic(origin, (row["latitude"], row["longitude"])).km, 3
        ), axis=1
    )

    # Filter by radius
    nearby = df[df["distance_km"] <= radius_km].copy()
    nearby = nearby.sort_values("distance_km")

    # Summary counts by type
    counts = nearby["asset_type"].value_counts().to_dict()

    # Top 3 closest per type
    details = {}
    for atype in nearby["asset_type"].unique():
        subset = nearby[nearby["asset_type"] == atype].head(3)
        details[atype] = [
            {
                "asset_id"   : row["asset_id"],
                "distance_km": row["distance_km"],
                "latitude"   : row["latitude"],
                "longitude"  : row["longitude"],
            }
            for _, row in subset.iterrows()
        ]

    return {
        "center"          : {"latitude": latitude, "longitude": longitude},
        "radius_km"       : radius_km,
        "total_assets"    : len(nearby),
        "counts_by_type"  : counts,
        "nearest_assets"  : details,
        "critical_assets" : {
            "hospitals"        : counts.get("hospital",         0),
            "schools"          : counts.get("school",           0),
            "emergency_centers": counts.get("emergency_center", 0),
            "shelters"         : counts.get("shelter",          0),
        }
    }

# ── Tool 2: Compute Distance ──────────────────────────────
@Tool
def compute_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> dict:
    """
    Compute the geodesic distance between two coordinates.
    Returns distance in km and miles.
    Args:
        lat1: Latitude of point 1
        lon1: Longitude of point 1
        lat2: Latitude of point 2
        lon2: Longitude of point 2
    """
    dist_km    = geodesic((lat1, lon1), (lat2, lon2)).km
    dist_miles = dist_km * 0.621371

    return {
        "distance_km"   : round(dist_km,    3),
        "distance_miles": round(dist_miles, 3),
        "point1"        : {"latitude": lat1, "longitude": lon1},
        "point2"        : {"latitude": lat2, "longitude": lon2},
    }

# ── Tool 3: Estimate Population Exposure ─────────────────
@Tool
def estimate_population_exposure(
    latitude  : float,
    longitude : float,
    radius_km : float = 5.0
) -> dict:
    """
    Estimate the number of people potentially exposed
    to wildfire risk within a given radius.
    Uses house count as population proxy.
    Args:
        latitude: Fire origin latitude
        longitude: Fire origin longitude
        radius_km: Impact radius in kilometers
    """
    df     = _get_infra_df().copy()
    origin = (latitude, longitude)

    df["distance_km"] = df.apply(
        lambda row: geodesic(
            origin, (row["latitude"], row["longitude"])
        ).km, axis=1
    )

    nearby   = df[df["distance_km"] <= radius_km]
    n_houses = len(nearby[nearby["asset_type"] == "house"])

    # California avg household size: 2.9 people
    est_pop  = n_houses * 2.9

    return {
        "radius_km"           : radius_km,
        "estimated_houses"    : n_houses,
        "estimated_population": round(est_pop),
        "hospitals_at_risk"   : len(nearby[nearby["asset_type"] == "hospital"]),
        "schools_at_risk"     : len(nearby[nearby["asset_type"] == "school"]),
        "shelters_available"  : len(nearby[nearby["asset_type"] == "shelter"]),
        "evacuation_note"     : (
            f"Approximately {round(est_pop):,} people in "
            f"{n_houses} households within {radius_km}km radius"
        )
    }
