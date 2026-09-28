import pandas as pd


# ============================================================
# FILES
# ============================================================

BASE_FILE = "data/processed/final_regime_features_july_2024.csv"

GEO_FILE = "data/geography/gfs_geographic_features.csv"

TERRAIN_FILE = "data/geography/gfs_terrain_features.csv"

OUTPUT_FILE = "data/processed/final_regime_features_july_2024.csv"


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("LOADING FILES")
print("=" * 70)

base = pd.read_csv(BASE_FILE)

geo = pd.read_csv(GEO_FILE)

terrain = pd.read_csv(TERRAIN_FILE)

print("Base:", base.shape)
print("Geographic:", geo.shape)
print("Terrain:", terrain.shape)


# ============================================================
# CHECK SOURCE COLUMNS
# ============================================================

print("\nGeographic columns:")
print(geo.columns.tolist())

print("\nTerrain columns:")
print(terrain.columns.tolist())


# ============================================================
# CHECK DUPLICATES
# ============================================================

geo_duplicates = geo.duplicated(
    ["latitude", "longitude"]
).sum()

terrain_duplicates = terrain.duplicated(
    ["latitude", "longitude"]
).sum()

print("\nGeographic duplicates:", geo_duplicates)
print("Terrain duplicates:", terrain_duplicates)

if geo_duplicates > 0:
    raise ValueError(
        "Duplicate latitude/longitude values in geographic file."
    )

if terrain_duplicates > 0:
    raise ValueError(
        "Duplicate latitude/longitude values in terrain file."
    )


# ============================================================
# REMOVE OLD VERSIONS IF PRESENT
# ============================================================

for col in [
    "elevation",
    "elevation_m",
    "coast_distance_km",
    "slope",
    "terrain_slope_deg"
]:

    if col in base.columns:
        base = base.drop(columns=[col])


# ============================================================
# MERGE ELEVATION + COAST DISTANCE
# ============================================================

print("\nMerging elevation and coast distance...")

geo_small = geo[
    [
        "latitude",
        "longitude",
        "elevation_m",
        "coast_distance_km"
    ]
].copy()

geo_small = geo_small.rename(
    columns={
        "elevation_m": "elevation"
    }
)

base = base.merge(
    geo_small,
    on=[
        "latitude",
        "longitude"
    ],
    how="left",
    validate="many_to_one"
)


# ============================================================
# MERGE TERRAIN SLOPE
# ============================================================

print("Merging terrain slope...")

terrain_small = terrain[
    [
        "latitude",
        "longitude",
        "terrain_slope_deg"
    ]
].copy()

terrain_small = terrain_small.rename(
    columns={
        "terrain_slope_deg": "slope"
    }
)

base = base.merge(
    terrain_small,
    on=[
        "latitude",
        "longitude"
    ],
    how="left",
    validate="many_to_one"
)


# ============================================================
# CHECK RESULT
# ============================================================

print("\n" + "=" * 70)
print("CHECKING MERGED DATA")
print("=" * 70)

print("Final shape:", base.shape)


geo_features = [
    "elevation",
    "coast_distance_km",
    "slope"
]


for col in geo_features:

    print(f"\n{col}")

    print(
        "  Missing:",
        base[col].isna().sum()
    )

    print(
        "  Min:",
        base[col].min()
    )

    print(
        "  Max:",
        base[col].max()
    )

    print(
        "  Mean:",
        base[col].mean()
    )


# ============================================================
# FAIL IF MISSING
# ============================================================

missing_total = (
    base[geo_features]
    .isna()
    .sum()
    .sum()
)

if missing_total > 0:

    raise ValueError(
        f"Geographic merge produced "
        f"{missing_total} missing values."
    )


# ============================================================
# CHECK DATE/GRID DUPLICATES
# ============================================================

duplicates = base.duplicated(
    [
        "date",
        "latitude",
        "longitude"
    ]
).sum()

print(
    "\nDate/grid duplicates:",
    duplicates
)

if duplicates > 0:

    raise ValueError(
        "Duplicate date/grid records detected."
    )


# ============================================================
# SAVE
# ============================================================

base.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print("Saved:", OUTPUT_FILE)

print("Shape:", base.shape)

print("\nAdded features:")

print("  elevation")
print("  coast_distance_km")
print("  slope")