import pandas as pd


REGIME_FILE = (
    "data/processed/"
    "regime_features_july_2024.csv"
)

GEO_FILE = (
    "data/geography/"
    "gfs_geographic_features.csv"
)

OUTPUT_FILE = (
    "data/processed/"
    "regime_features_with_geography_july_2024.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading atmospheric/regime features...")

regime = pd.read_csv(
    REGIME_FILE,
    parse_dates=["date"]
)

print(
    f"Atmospheric dataset: {regime.shape}"
)


print("\nLoading geographic features...")

geo = pd.read_csv(
    GEO_FILE
)

print(
    f"Geographic dataset: {geo.shape}"
)


# ============================================================
# CHECK GEOGRAPHIC GRID
# ============================================================

duplicates = geo.duplicated(
    subset=["latitude", "longitude"]
).sum()

print(
    f"\nGeographic duplicate grid cells: {duplicates}"
)

if duplicates != 0:
    raise ValueError(
        "Duplicate latitude/longitude values found."
    )


# ============================================================
# MERGE
# ============================================================

print("\nMerging geographic features...")

merged = regime.merge(
    geo[
        [
            "latitude",
            "longitude",
            "elevation_m",
            "coast_distance_km"
        ]
    ],
    on=[
        "latitude",
        "longitude"
    ],
    how="left",
    validate="many_to_one"
)


# ============================================================
# CHECK
# ============================================================

print(
    f"\nDataset after merge: {merged.shape}"
)


missing = merged[
    [
        "elevation_m",
        "coast_distance_km"
    ]
].isna().sum()

print("\nMissing geographic values:")
print(missing)


if missing.sum() != 0:
    raise ValueError(
        "Some rows are missing geographic features."
    )


duplicates = merged.duplicated(
    subset=[
        "date",
        "latitude",
        "longitude"
    ]
).sum()

print(
    "\nDuplicate date/grid observations:",
    duplicates
)


# ============================================================
# SAVE
# ============================================================

merged.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("=" * 65)
print("GEOGRAPHIC FEATURES MERGED SUCCESSFULLY")
print("=" * 65)

print(
    f"Rows    : {len(merged):,}"
)

print(
    f"Columns : {len(merged.columns)}"
)

print(
    f"Output  : {OUTPUT_FILE}"
)

print("=" * 65)