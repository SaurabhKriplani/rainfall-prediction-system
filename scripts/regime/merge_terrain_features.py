import pandas as pd

MAIN = "data/processed/final_regime_features_july_2024.csv"
TERRAIN = "data/geography/gfs_terrain_features.csv"

OUTPUT = "data/processed/final_regime_features_july_2024.csv"

# --------------------------------------------------
# Load
# --------------------------------------------------

main = pd.read_csv(MAIN)
terrain = pd.read_csv(TERRAIN)

print("Main dataset:", main.shape)
print("Terrain dataset:", terrain.shape)

# --------------------------------------------------
# Check terrain uniqueness
# --------------------------------------------------

duplicate_terrain = terrain.duplicated(
    subset=["latitude", "longitude"]
).sum()

print("Duplicate terrain grid cells:", duplicate_terrain)

# --------------------------------------------------
# Merge
# --------------------------------------------------

main = main.merge(
    terrain[
        [
            "latitude",
            "longitude",
            "terrain_slope_deg"
        ]
    ],
    on=["latitude", "longitude"],
    how="left",
    validate="many_to_one"
)

# --------------------------------------------------
# Validation
# --------------------------------------------------

print("\nFinal shape:")
print(main.shape)

print("\nMissing terrain slope:")
print(main["terrain_slope_deg"].isna().sum())

print("\nTerrain slope statistics:")
print(main["terrain_slope_deg"].describe())

print("\nDuplicate date/grid observations:")

duplicates = main.duplicated(
    subset=["date", "latitude", "longitude"]
).sum()

print(duplicates)

# --------------------------------------------------
# Save
# --------------------------------------------------

main.to_csv(OUTPUT, index=False)

print("\nSaved:")
print(OUTPUT)