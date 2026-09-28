import pandas as pd

INPUT = "data/processed/regime_features_with_geography_july_2024.csv"
OUTPUT = "data/processed/final_regime_features_july_2024.csv"

df = pd.read_csv(INPUT)
df["date"] = pd.to_datetime(df["date"])


def assign_synoptic_regime(date):
    day = date.day

    # IMD-documented July 2024 low-pressure systems
    if 15 <= day <= 17:
        return "low_pressure"

    if day == 18:
        return "low_pressure"

    # Depression phase
    if 19 <= day <= 20:
        return "depression"

    if 21 <= day <= 23:
        return "low_pressure"

    if 26 <= day <= 28:
        return "low_pressure"

    # No documented July 2024 break monsoon.
    # These are retained as background monsoon states rather
    # than assigning unsupported active/break labels.
    return "background_monsoon"


df["synoptic_regime"] = df["date"].apply(assign_synoptic_regime)

# Local geographic context.
# Keep these as continuous variables for ML rather than
# imposing arbitrary coastal/orographic thresholds.
df["coastal_proximity"] = df["coast_distance_km"]

df["terrain_elevation"] = df["elevation_m"]


print("\nSynoptic regime counts:")
print(df[["date", "synoptic_regime"]]
      .drop_duplicates()
      .groupby("synoptic_regime")
      .size())

print("\nDates by regime:")
print(
    df[["date", "synoptic_regime"]]
    .drop_duplicates()
    .sort_values("date")
    .to_string(index=False)
)

print("\nFinal shape:")
print(df.shape)

print("\nMissing values:")
print(df.isna().sum().sum())

df.to_csv(OUTPUT, index=False)

print(f"\nSaved to: {OUTPUT}")