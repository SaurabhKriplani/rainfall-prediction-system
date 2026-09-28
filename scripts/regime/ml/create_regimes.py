import pandas as pd
import numpy as np

# ============================================================
# 1. LOAD DATA
# ============================================================

INPUT = "data/final/master_training_jul_sep_2024.csv"
OUTPUT = "data/final/master_regime_jul_sep_2024.csv"

df = pd.read_csv(INPUT)

print("Loaded:", df.shape)


# ============================================================
# 2. CREATE SIMPLE ATMOSPHERIC FEATURES
# ============================================================

# Wind speed at 850 hPa
df["wind850"] = np.sqrt(
    df["u850"]**2 + df["v850"]**2
)

# Wind speed at 500 hPa
df["wind500"] = np.sqrt(
    df["u500"]**2 + df["v500"]**2
)

# Vertical wind / upward motion indicator
# ERA5 vertical velocity: negative generally indicates upward motion
df["upward_motion"] = -df["w700"]

# Moisture indicator
df["moisture"] = (
    df["r850"] +
    df["r700"] +
    df["r500"]
) / 3

# Vertical wind shear
df["wind_shear"] = np.sqrt(
    (df["u200"] if "u200" in df.columns else df["u500"] - df["u850"])**2 +
    (df["v200"] if "v200" in df.columns else df["v500"] - df["v850"])**2
)

# Geopotential difference
df["z_gradient"] = df["z500"] - df["z850"]


# ============================================================
# 3. DAILY CONDITIONS
# ============================================================

daily = df.groupby("date").agg({

    "gfs_rain_24h": "mean",
    "imd_rainfall": "mean",

    "r500": "mean",
    "r700": "mean",
    "r850": "mean",

    "wind850": "mean",
    "wind500": "mean",

    "upward_motion": "mean",
    "moisture": "mean",

    "wind_shear": "mean",
    "z_gradient": "mean"
}).reset_index()


# ============================================================
# 4. SIMPLE REGIME CLASSIFICATION
# ============================================================

def classify_regime(row):

    rainfall = row["imd_rainfall"]
    moisture = row["moisture"]
    upward = row["upward_motion"]
    wind = row["wind850"]

    # --------------------------------------------------------
    # 1. Active Monsoon
    # --------------------------------------------------------
    if rainfall >= 10 and moisture >= 70:
        return "Active Monsoon"

    # --------------------------------------------------------
    # 2. Break Monsoon
    # --------------------------------------------------------
    if rainfall < 5 and moisture < 65:
        return "Break Monsoon"

    # --------------------------------------------------------
    # 3. Monsoon Low / Depression
    # --------------------------------------------------------
    if upward > 0.05 and moisture >= 70:
        return "Monsoon Low/Depression"

    # --------------------------------------------------------
    # 4. Coastal Rainfall
    # --------------------------------------------------------
    # High moisture + rainfall
    if rainfall >= 10 and moisture >= 75:
        return "Coastal Rainfall"

    # --------------------------------------------------------
    # 5. Orographic Rainfall
    # --------------------------------------------------------
    if rainfall >= 10:
        return "Orographic Rainfall"

    # --------------------------------------------------------
    # 6. Western Disturbance
    # --------------------------------------------------------
    if row["z_gradient"] < -500:
        return "Western Disturbance"

    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------
    return "Break Monsoon"


daily["regime"] = daily.apply(classify_regime, axis=1)


# ============================================================
# 5. DISPLAY REGIME DISTRIBUTION
# ============================================================

print("\nREGIME DISTRIBUTION")
print("===================")

print(daily["regime"].value_counts())

print("\nPercentage:")
print(
    daily["regime"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# 6. MERGE DAILY REGIME BACK TO GRID DATA
# ============================================================

df = df.merge(
    daily[["date", "regime"]],
    on="date",
    how="left"
)


# ============================================================
# 7. REGIME NUMBER
# ============================================================

regime_map = {
    "Active Monsoon": 0,
    "Break Monsoon": 1,
    "Monsoon Low/Depression": 2,
    "Orographic Rainfall": 3,
    "Coastal Rainfall": 4,
    "Western Disturbance": 5
}

df["regime_id"] = df["regime"].map(regime_map)


# ============================================================
# 8. SAVE
# ============================================================

df.to_csv(OUTPUT, index=False)

print("\nSaved:")
print(OUTPUT)

print("\nFinal shape:")
print(df.shape)

print("\nFinal columns:")
print(df.columns.tolist())