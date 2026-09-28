import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from xgboost import XGBRegressor, XGBClassifier

# Directories
PROJECT_DIR = Path.cwd()
DATA_FILE = PROJECT_DIR / "data" / "final" / "master_regime_final_jul_sep_2024.csv"
MODELS_DIR = PROJECT_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("EXPORTING TRAINED XGBOOST MODELS FOR FASTAPI BACKEND")
print("=" * 70)

# Load master dataset
df = pd.read_csv(DATA_FILE)
df["date"] = pd.to_datetime(df["date"])

print(f"Loaded dataset shape: {df.shape}")
print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} -> {df['date'].max().strftime('%Y-%m-%d')}")

# Feature ordering MUST be identical across all model training & inference
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

# Time-based split: Train on July + August 2024
train = df[df["date"] < "2024-09-01"].copy()
print(f"Train subset shape: {train.shape}")

X_train = train[FEATURES]

# ------------------------------------------------------------
# 1. BIAS CORRECTION MODEL (XGBRegressor)
# ------------------------------------------------------------
print("\n1. Training & Exporting Bias Correction Model (XGBRegressor)...")
y_bias = train["bias"]

bias_model = XGBRegressor(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)
bias_model.fit(X_train, y_bias)

bias_model_path = MODELS_DIR / "bias_correction_model.pkl"
joblib.dump(bias_model, bias_model_path)
print(f"Saved: {bias_model_path}")

# ------------------------------------------------------------
# 2. HEAVY RAINFALL PROBABILITY MODELS (XGBClassifier)
# ------------------------------------------------------------
thresholds = [
    (64.5, "heavy_rain_model.pkl", "Heavy Rainfall (>=64.5mm)"),
    (115.6, "very_heavy_rain_model.pkl", "Very Heavy Rainfall (>=115.6mm)"),
    (204.5, "extremely_heavy_rain_model.pkl", "Extremely Heavy Rainfall (>=204.5mm)")
]

for thresh, filename, label in thresholds:
    print(f"\nTraining & Exporting {label} Classifier...")
    y_class = (train["imd_rainfall"] >= thresh).astype(int)
    
    pos = y_class.sum()
    neg = len(y_class) - pos
    scale_weight = (neg / pos) if pos > 0 else 1.0
    
    clf = XGBClassifier(
        n_estimators=300,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        scale_pos_weight=scale_weight,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_class)
    
    out_path = MODELS_DIR / filename
    joblib.dump(clf, out_path)
    print(f"Saved: {out_path}")

print("\n" + "=" * 70)
print("ALL 4 MODELS EXPORTED SUCCESSFULLY!")
print("=" * 70)
