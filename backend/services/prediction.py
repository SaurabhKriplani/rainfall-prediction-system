import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from backend.services.regime import classify_regime

# Project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_DIR / "models"

FEATURES = [
    "gfs_rain_24h",
    "latitude",
    "longitude",
    "r500", "r700", "r850",
    "t500", "t700", "t850",
    "u500", "u700", "u850",
    "v500", "v700", "v850",
    "w500", "w700", "w850",
    "z500", "z700", "z850",
    "regime_id_final"
]

class PredictionService:
    def __init__(self):
        self.bias_model = None
        self.heavy_model = None
        self.very_heavy_model = None
        self.extremely_heavy_model = None
        self.models_loaded = False

    def load_models(self):
        """Loads all 4 XGBoost models ONCE at application startup."""
        print("Loading XGBoost models from models/ directory...")
        bias_path = MODELS_DIR / "bias_correction_model.pkl"
        heavy_path = MODELS_DIR / "heavy_rain_model.pkl"
        very_heavy_path = MODELS_DIR / "very_heavy_rain_model.pkl"
        extremely_heavy_path = MODELS_DIR / "extremely_heavy_rain_model.pkl"

        if not (bias_path.exists() and heavy_path.exists() and very_heavy_path.exists() and extremely_heavy_path.exists()):
            raise FileNotFoundError(f"One or more model files missing in {MODELS_DIR}")

        self.bias_model = joblib.load(bias_path)
        self.heavy_model = joblib.load(heavy_path)
        self.very_heavy_model = joblib.load(very_heavy_path)
        self.extremely_heavy_model = joblib.load(extremely_heavy_path)
        self.models_loaded = True
        print("All 4 XGBoost models successfully loaded into memory!")

    def predict_single(self, input_data: dict) -> dict:
        """
        Executes bias correction and heavy rainfall risk prediction for a single point.
        """
        if not self.models_loaded:
            self.load_models()

        lat = float(input_data["latitude"])
        lon = float(input_data["longitude"])
        gfs_rain = float(input_data["gfs_rain_24h"])

        # Determine regime if not directly provided
        if input_data.get("regime_id") is not None and input_data.get("regime") is not None:
            regime_name = input_data["regime"]
            regime_id = int(input_data["regime_id"])
        else:
            regime_info = classify_regime(
                lat=lat,
                lon=lon,
                gfs_rain_24h=gfs_rain,
                r500=float(input_data["r500"]),
                r700=float(input_data["r700"]),
                r850=float(input_data["r850"]),
                w700=float(input_data["w700"]),
                z500=float(input_data["z500"]),
                z850=float(input_data["z850"])
            )
            regime_name = regime_info["regime_name"]
            regime_id = regime_info["regime_id"]

        # Construct input row matching exact feature order
        row_dict = {
            "gfs_rain_24h": gfs_rain,
            "latitude": lat,
            "longitude": lon,
            "r500": float(input_data["r500"]),
            "r700": float(input_data["r700"]),
            "r850": float(input_data["r850"]),
            "t500": float(input_data["t500"]),
            "t700": float(input_data["t700"]),
            "t850": float(input_data["t850"]),
            "u500": float(input_data["u500"]),
            "u700": float(input_data["u700"]),
            "u850": float(input_data["u850"]),
            "v500": float(input_data["v500"]),
            "v700": float(input_data["v700"]),
            "v850": float(input_data["v850"]),
            "w500": float(input_data["w500"]),
            "w700": float(input_data["w700"]),
            "w850": float(input_data["w850"]),
            "z500": float(input_data["z500"]),
            "z700": float(input_data["z700"]),
            "z850": float(input_data["z850"]),
            "regime_id_final": regime_id
        }

        X_input = pd.DataFrame([row_dict])[FEATURES]

        # 1. Bias prediction & corrected rainfall
        predicted_bias = float(self.bias_model.predict(X_input)[0])
        corrected_rainfall = max(0.0, float(gfs_rain + predicted_bias))

        # 2. Probability predictions
        heavy_prob = float(self.heavy_model.predict_proba(X_input)[0][1])
        very_heavy_prob = float(self.very_heavy_model.predict_proba(X_input)[0][1])
        extremely_heavy_prob = float(self.extremely_heavy_model.predict_proba(X_input)[0][1])

        return {
            "regime": regime_name,
            "regime_id": regime_id,
            "gfs_rainfall_mm": round(gfs_rain, 2),
            "predicted_bias_mm": round(predicted_bias, 2),
            "corrected_rainfall_mm": round(corrected_rainfall, 2),
            "heavy_probability": round(heavy_prob, 4),
            "very_heavy_probability": round(very_heavy_prob, 4),
            "extremely_heavy_probability": round(extremely_heavy_prob, 4)
        }

# Global service instance
prediction_service = PredictionService()
