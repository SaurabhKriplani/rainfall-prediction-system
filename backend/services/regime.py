import numpy as np
import pandas as pd

REGIME_MAP = {
    "Active Monsoon": 0,
    "Break Monsoon": 1,
    "Monsoon Low/Depression": 2,
    "Orographic Rainfall": 3,
    "Coastal Rainfall": 4,
    "Western Disturbance": 5
}

REGIME_DETAILS = [
    {
        "id": 0,
        "name": "Active Monsoon",
        "description": "Widespread monsoon rainfall driven by active trough position, high moisture (RH > 70%), and strong low-level westerly monsoon flow.",
        "samples_2024": 127600,
        "days_represented": 28
    },
    {
        "id": 1,
        "name": "Break Monsoon",
        "description": "Monsoon trough shifts north to Himalayan foothills resulting in suppressed rainfall over central India and reduced moisture (RH < 65%).",
        "samples_2024": 154750,
        "days_represented": 34
    },
    {
        "id": 2,
        "name": "Monsoon Low/Depression",
        "description": "Cyclonic vortex / low-pressure system forming in Bay of Bengal or land with intense upward motion (-w700 > 0.05 Pa/s) and heavy rainfall.",
        "samples_2024": 63700,
        "days_represented": 14
    },
    {
        "id": 3,
        "name": "Orographic Rainfall",
        "description": "Forced topographic ascent of moist monsoon winds along Western Ghats (8–21°N, 72.5–76.5°E) and Himalayan region (27–35°N, 73–97°E).",
        "samples_2024": 45500,
        "days_represented": 10
    },
    {
        "id": 4,
        "name": "Coastal Rainfall",
        "description": "Convective and boundary layer moisture convergence along east/west maritime coastline regions (lon <= 75.5°E or >= 88°E, lat <= 23°N).",
        "samples_2024": 33950,
        "days_represented": 6
    },
    {
        "id": 5,
        "name": "Western Disturbance",
        "description": "Extratropical synoptic systems originating over the Mediterranean. Supported by the system framework but 0 genuine samples exist during July–September 2024 monsoon.",
        "samples_2024": 0,
        "days_represented": 0,
        "note": "Western Disturbance is supported by the system but is not represented in the selected July–September 2024 training period."
    }
]

def classify_regime(
    lat: float,
    lon: float,
    gfs_rain_24h: float,
    r500: float,
    r700: float,
    r850: float,
    w700: float,
    z500: float,
    z850: float
) -> dict:
    """
    Classifies a grid point into one of the 6 synoptic weather regimes
    matching the exact logic from script preprocessing pipeline.
    """
    moisture = (r850 + r700 + r500) / 3.0
    upward_motion = -w700
    z_gradient = z500 - z850

    # 1. Spatial Check: Orographic (Western Ghats & Himalayas)
    western_ghats = (8.0 <= lat <= 21.0) and (72.5 <= lon <= 76.5)
    himalayas = (27.0 <= lat <= 35.0) and (73.0 <= lon <= 97.0)
    is_orographic = western_ghats or himalayas

    # 2. Spatial Check: Coastal
    is_coastal = ((lon <= 75.5) or (lon >= 88.0)) and (lat <= 23.0)

    # 3. Western Disturbance condition
    is_wd = (lat >= 28.0) and (z_gradient < -500.0)

    regime_name = "Break Monsoon"

    if is_orographic:
        regime_name = "Orographic Rainfall"
    elif is_coastal:
        regime_name = "Coastal Rainfall"
    elif is_wd:
        regime_name = "Western Disturbance"
    else:
        # Synoptic atmospheric classification
        if gfs_rain_24h >= 10.0 and moisture >= 70.0:
            regime_name = "Active Monsoon"
        elif gfs_rain_24h < 5.0 and moisture < 65.0:
            regime_name = "Break Monsoon"
        elif upward_motion > 0.05 and moisture >= 70.0:
            regime_name = "Monsoon Low/Depression"
        elif gfs_rain_24h >= 10.0 and moisture >= 75.0:
            regime_name = "Coastal Rainfall"
        elif gfs_rain_24h >= 10.0:
            regime_name = "Orographic Rainfall"
        elif z_gradient < -500.0:
            regime_name = "Western Disturbance"
        else:
            regime_name = "Break Monsoon"

    regime_id = REGIME_MAP.get(regime_name, 1)

    return {
        "regime_name": regime_name,
        "regime_id": regime_id,
        "moisture_mean": round(float(moisture), 2),
        "upward_motion": round(float(upward_motion), 4),
        "z_gradient": round(float(z_gradient), 2)
    }
