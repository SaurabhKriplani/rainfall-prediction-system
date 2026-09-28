import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "processed" / "gfs_era5_imd_july_2024.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "regime_features_july_2024.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("Loading dataset...")

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

print(f"Input shape: {df.shape}")


# ============================================================
# 1. WIND SPEED
# ============================================================

df["wind850"] = np.sqrt(
    df["u850"]**2 + df["v850"]**2
)

df["wind700"] = np.sqrt(
    df["u700"]**2 + df["v700"]**2
)

df["wind500"] = np.sqrt(
    df["u500"]**2 + df["v500"]**2
)


# ============================================================
# 2. WIND DIRECTION
# ============================================================

df["wind_dir850"] = (
    np.degrees(
        np.arctan2(-df["u850"], -df["v850"])
    ) + 360
) % 360


# ============================================================
# 3. VERTICAL MOTION
# ============================================================

# ERA5 omega (w) convention:
# negative = upward motion
# positive = downward motion

df["upward_motion850"] = -df["w850"]
df["upward_motion700"] = -df["w700"]
df["upward_motion500"] = -df["w500"]


# ============================================================
# 4. MOISTURE FEATURES
# ============================================================

# Mean relative humidity through the lower/middle atmosphere

df["rh_lower_mid"] = (
    df["r850"] * 0.5 +
    df["r700"] * 0.3 +
    df["r500"] * 0.2
)


# Moisture difference between lower and upper levels

df["rh850_rh500_diff"] = df["r850"] - df["r500"]


# ============================================================
# 5. TEMPERATURE FEATURES
# ============================================================

df["t850_t500_diff"] = df["t850"] - df["t500"]

df["t850_t700_diff"] = df["t850"] - df["t700"]


# ============================================================
# 6. VERTICAL WIND SHEAR
# ============================================================

df["shear850_500"] = np.sqrt(
    (df["u500"] - df["u850"])**2 +
    (df["v500"] - df["v850"])**2
)


df["shear850_700"] = np.sqrt(
    (df["u700"] - df["u850"])**2 +
    (df["v700"] - df["v850"])**2
)


# ============================================================
# 7. WIND SPEED DIFFERENCES
# ============================================================

df["wind850_500_diff"] = df["wind850"] - df["wind500"]

df["wind850_700_diff"] = df["wind850"] - df["wind700"]


# ============================================================
# 8. DAILY DOMAIN-LEVEL FEATURES
# ============================================================

# These represent the atmospheric state over the whole
# GFS/ERA5 domain for each day.

daily_features = (
    df.groupby("date")
    .agg(
        mean_wind850=("wind850", "mean"),
        mean_wind700=("wind700", "mean"),
        mean_wind500=("wind500", "mean"),

        mean_rh850=("r850", "mean"),
        mean_rh700=("r700", "mean"),
        mean_rh500=("r500", "mean"),

        mean_rh_lower_mid=("rh_lower_mid", "mean"),

        mean_upward850=("upward_motion850", "mean"),
        mean_upward700=("upward_motion700", "mean"),
        mean_upward500=("upward_motion500", "mean"),

        mean_shear850_500=("shear850_500", "mean"),

        mean_t850=("t850", "mean"),
        mean_t700=("t700", "mean"),
        mean_t500=("t500", "mean"),

        mean_gfs_rain=("gfs_rain_24h", "mean"),
        mean_imd_rain=("imd_rainfall", "mean"),
        mean_bias=("bias", "mean"),

        max_gfs_rain=("gfs_rain_24h", "max"),
        max_imd_rain=("imd_rainfall", "max"),
    )
    .reset_index()
)


# ============================================================
# 9. ADD DAILY FEATURES BACK TO GRID DATA
# ============================================================

df = df.merge(
    daily_features,
    on="date",
    how="left"
)


# ============================================================
# 10. SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n========================================")
print("REGIME FEATURE GENERATION COMPLETE")
print("========================================")

print(f"Output: {OUTPUT_FILE}")
print(f"Shape: {df.shape}")

print("\nNew regime-related features:")

new_features = [
    "wind850",
    "wind700",
    "wind500",
    "wind_dir850",
    "upward_motion850",
    "upward_motion700",
    "upward_motion500",
    "rh_lower_mid",
    "rh850_rh500_diff",
    "t850_t500_diff",
    "t850_t700_diff",
    "shear850_500",
    "shear850_700",
    "wind850_500_diff",
    "wind850_700_diff",
]

print(new_features)

print("\nDaily atmospheric summary:")
print(daily_features.round(3).to_string(index=False))