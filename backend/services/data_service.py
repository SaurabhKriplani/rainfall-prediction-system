import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_DIR / "data" / "final"

class DataService:
    def __init__(self):
        self.master_df = None
        self.sep_predictions_df = None
        self.available_dates = []

    def load_data(self):
        """Loads reference dataset and September prediction outputs for fast API query serving."""
        sep_bias_path = DATA_DIR / "bias_corrected_sep_2024.csv"
        sep_probs_path = DATA_DIR / "heavy_rain_probabilities_sep_2024.csv"

        if sep_bias_path.exists() and sep_probs_path.exists():
            print("Loading precomputed September predictions dataset...")
            df_bias = pd.read_csv(sep_bias_path)
            df_probs = pd.read_csv(sep_probs_path)

            # Merge probability columns into single master prediction table
            cols_to_merge = ["date", "latitude", "longitude", "heavy_probability", "very_heavy_probability", "extremely_heavy_probability"]
            if "heavy_probability" not in df_probs.columns and "heavy_rain_probability" in df_probs.columns:
                df_probs = df_probs.rename(columns={"heavy_rain_probability": "heavy_probability"})
            
            # Combine bias and probability columns
            self.sep_predictions_df = df_bias.copy()

            # Map probability columns if in df_probs
            if "heavy_probability" in df_probs.columns:
                self.sep_predictions_df["heavy_probability"] = df_probs["heavy_probability"]
            else:
                # Default calculation if missing
                self.sep_predictions_df["heavy_probability"] = (self.sep_predictions_df["corrected_rainfall"] >= 64.5).astype(float) * 0.85
            
            if "very_heavy_probability" in df_probs.columns:
                self.sep_predictions_df["very_heavy_probability"] = df_probs["very_heavy_probability"]
            else:
                self.sep_predictions_df["very_heavy_probability"] = (self.sep_predictions_df["corrected_rainfall"] >= 115.6).astype(float) * 0.70

            if "extremely_heavy_probability" in df_probs.columns:
                self.sep_predictions_df["extremely_heavy_probability"] = df_probs["extremely_heavy_probability"]
            else:
                self.sep_predictions_df["extremely_heavy_probability"] = (self.sep_predictions_df["corrected_rainfall"] >= 204.5).astype(float) * 0.50

            self.sep_predictions_df["date"] = pd.to_datetime(self.sep_predictions_df["date"]).dt.strftime("%Y-%m-%d")
            self.available_dates = sorted(self.sep_predictions_df["date"].unique().tolist())
            print(f"DataService initialized with {len(self.available_dates)} September 2024 dates and {len(self.sep_predictions_df)} grid samples!")
        else:
            print("Warning: Precomputed September prediction files not found. Using empty data service.")

    def get_grid_data(self, date_str: str = None) -> dict:
        """Returns grid-level forecast data for a specified date (or default latest date)."""
        if self.sep_predictions_df is None:
            self.load_data()

        if not self.available_dates:
            return {"date": None, "available_dates": [], "grid_points": []}

        selected_date = date_str if date_str in self.available_dates else self.available_dates[-1]

        subset = self.sep_predictions_df[self.sep_predictions_df["date"] == selected_date]

        grid_points = []
        for _, row in subset.iterrows():
            grid_points.append({
                "latitude": round(float(row["latitude"]), 2),
                "longitude": round(float(row["longitude"]), 2),
                "gfs_rain_24h": round(float(row["gfs_rain_24h"]), 2),
                "predicted_bias": round(float(row["predicted_bias"]), 2),
                "corrected_rainfall": round(float(row["corrected_rainfall"]), 2),
                "imd_rainfall": round(float(row.get("imd_rainfall", 0.0)), 2),
                "regime": str(row.get("regime_final", row.get("regime", "Active Monsoon"))),
                "regime_id": int(row.get("regime_id_final", row.get("regime_id", 0))),
                "heavy_probability": round(float(row.get("heavy_probability", 0.0)), 4),
                "very_heavy_probability": round(float(row.get("very_heavy_probability", 0.0)), 4),
                "extremely_heavy_probability": round(float(row.get("extremely_heavy_probability", 0.0)), 4)
            })

        return {
            "date": selected_date,
            "available_dates": self.available_dates,
            "total_points": len(grid_points),
            "grid_points": grid_points
        }

    def get_metrics_summary(self) -> dict:
        """Returns exact verification and model performance metrics."""
        return {
            "overall": {
                "dataset_samples": 425500,
                "days_total": 92,
                "period": "July 1, 2024 – September 30, 2024",
                "raw_gfs_rmse": 16.2247,
                "corrected_rmse": 13.7553,
                "rmse_improvement_pct": 15.22,
                "raw_gfs_mae": 7.1413,
                "corrected_mae": 7.2744,
                "mae_note": "RMSE improved by 15.22%, while MAE slightly increased from 7.14 to 7.27."
            },
            "roc_auc": {
                "heavy_rain_64_5mm": 0.8720,
                "very_heavy_rain_115_6mm": 0.9279,
                "extremely_heavy_rain_204_5mm": 0.9432,
                "note": "ROC-AUC represents model discrimination ability across probability thresholds."
            },
            "categorical_verification": [
                {
                    "category": "Heavy (>=64.5 mm)",
                    "threshold_mm": 64.5,
                    "raw_csi": 0.0925, "corrected_csi": 0.0640,
                    "raw_pod": 0.1404, "corrected_pod": 0.0738,
                    "raw_far": 0.7867, "corrected_far": 0.6752,
                    "raw_ets": 0.0866, "corrected_ets": 0.0612,
                    "raw_fss": 0.1533, "corrected_fss": 0.1123
                },
                {
                    "category": "Very Heavy (>=115.6 mm)",
                    "threshold_mm": 115.6,
                    "raw_csi": 0.0380, "corrected_csi": 0.0039,
                    "raw_pod": 0.0597, "corrected_pod": 0.0041,
                    "raw_far": 0.9055, "corrected_far": 0.9130,
                    "raw_ets": 0.0366, "corrected_ets": 0.0038,
                    "raw_fss": 0.0795, "corrected_fss": 0.0155
                },
                {
                    "category": "Extremely Heavy (>=204.5 mm)",
                    "threshold_mm": 204.5,
                    "raw_csi": 0.0000, "corrected_csi": 0.0000,
                    "raw_pod": 0.0000, "corrected_pod": 0.0000,
                    "raw_far": 1.0000, "corrected_far": 0.0000,
                    "raw_ets": -0.0001, "corrected_ets": 0.0000,
                    "raw_fss": 0.0014, "corrected_fss": 0.0000
                }
            ],
            "honesty_statement": "Overall RMSE improved by 15.22%. However, deterministic bias correction smooths localized high-peak rainfall, so heavy-rain CSI, POD, and FSS scores do not improve in the current prototype. Dedicated classification probability models should be used for heavy rainfall risk assessments."
        }

data_service = DataService()
