import pandas as pd
import numpy as np

INPUT = "data/final/master_regime_jul_sep_2024.csv"
OUTPUT = "data/final/master_regime_final_jul_sep_2024.csv"

df = pd.read_csv(INPUT)

print("Loaded:", df.shape)


# ============================================================
# 1. COASTAL REGIME
# ============================================================
# Approximate coastal belt using longitude/latitude.
# This is a prototype spatial classification.

coastal = (
    (df["longitude"] <= 75.5) |
    (df["longitude"] >= 88.0)
) & (
    (df["latitude"] <= 23.0)
)


# ============================================================
# 2. OROGRAPHIC REGIME
# ============================================================
# Approximate major mountainous/orographic regions of India.
#
# Western Ghats:
# latitude roughly 8–21 N
# longitude roughly 73–76 E
#
# Himalayas:
# latitude roughly 27–35 N
# longitude roughly 73–97 E

western_ghats = (
    (df["latitude"] >= 8) &
    (df["latitude"] <= 21) &
    (df["longitude"] >= 72.5) &
    (df["longitude"] <= 76.5)
)

himalayas = (
    (df["latitude"] >= 27) &
    (df["latitude"] <= 35) &
    (df["longitude"] >= 73) &
    (df["longitude"] <= 97)
)

orographic = western_ghats | himalayas


# ============================================================
# 3. CREATE FINAL REGIME
# ============================================================

df["regime_final"] = df["regime"]


# Spatial regimes override the general daily regime
df.loc[orographic, "regime_final"] = "Orographic Rainfall"

df.loc[
    coastal & (~orographic),
    "regime_final"
] = "Coastal Rainfall"


# ============================================================
# 4. WESTERN DISTURBANCE
# ============================================================
# July–September is monsoon season, so we do NOT artificially
# create Western Disturbance examples.
#
# If atmospheric conditions indicate the pattern, retain it.
#
# A simple upper-level indicator is used here.

wd_condition = (
    (df["latitude"] >= 28) &
    (df["z_gradient"] < -500)
)

df.loc[
    wd_condition & (~orographic),
    "regime_final"
] = "Western Disturbance"


# ============================================================
# 5. FINAL REGIME IDs
# ============================================================

regime_map = {
    "Active Monsoon": 0,
    "Break Monsoon": 1,
    "Monsoon Low/Depression": 2,
    "Orographic Rainfall": 3,
    "Coastal Rainfall": 4,
    "Western Disturbance": 5
}

df["regime_id_final"] = df["regime_final"].map(regime_map)


# ============================================================
# 6. CHECK DISTRIBUTION
# ============================================================

print("\nFINAL REGIME DISTRIBUTION")
print("=========================")

print(df["regime_final"].value_counts())

print("\nPercentage:")

print(
    df["regime_final"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# 7. CHECK NUMBER OF DAYS
# ============================================================

print("\nREGIME DAYS")

daily_regime = (
    df.groupby(["date", "regime_final"])
    .size()
    .reset_index(name="samples")
)

print(
    daily_regime["regime_final"]
    .value_counts()
)


# ============================================================
# 8. SAVE
# ============================================================

df.to_csv(OUTPUT, index=False)

print("\nSaved:")
print(OUTPUT)

print("\nFinal shape:")
print(df.shape)

print("\nNew columns:")
print([
    "regime_final",
    "regime_id_final"
])