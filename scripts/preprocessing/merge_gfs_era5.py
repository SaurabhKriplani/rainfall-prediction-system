import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GFS_FILE = PROJECT_ROOT / "data" / "gfs" / "gfs_24h_july_2024.csv"
ERA5_FILE = PROJECT_ROOT / "data" / "era5" / "test" / "era5_features_test.csv"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "gfs_era5_july_2024.csv"


# --------------------------------------------------
# Load datasets
# --------------------------------------------------

print("Loading GFS...")
gfs = pd.read_csv(GFS_FILE)

print("Loading ERA5...")
era5 = pd.read_csv(ERA5_FILE)


# --------------------------------------------------
# Convert dates
# --------------------------------------------------

gfs["date"] = pd.to_datetime(
    gfs["date"],
    format="mixed"
)

era5["date"] = pd.to_datetime(
    era5["date"],
    format="mixed"
)


# --------------------------------------------------
# Keep ERA5 00 UTC
# --------------------------------------------------

era5 = era5[
    era5["date"].dt.hour == 0
].copy()


# --------------------------------------------------
# Restrict ERA5 to GFS domain
# --------------------------------------------------

era5 = era5[
    (era5["latitude"] >= 6) &
    (era5["latitude"] <= 38) &
    (era5["longitude"] >= 68) &
    (era5["longitude"] <= 98)
].copy()


# --------------------------------------------------
# Normalize coordinates
# --------------------------------------------------

gfs["latitude"] = gfs["latitude"].round(2)
gfs["longitude"] = gfs["longitude"].round(2)

era5["latitude"] = era5["latitude"].round(2)
era5["longitude"] = era5["longitude"].round(2)


# --------------------------------------------------
# Merge
# --------------------------------------------------

print("\nMerging GFS + ERA5...")

merged = pd.merge(
    gfs,
    era5,
    on=["date", "latitude", "longitude"],
    how="inner",
    validate="one_to_one"
)


# --------------------------------------------------
# Check result
# --------------------------------------------------

print("\nGFS shape:", gfs.shape)
print("ERA5 shape:", era5.shape)
print("Merged shape:", merged.shape)

expected_rows = 31 * 15609

print("Expected rows:", expected_rows)
print("Actual rows:", len(merged))

if len(merged) == expected_rows:
    print("\nSUCCESS: All GFS grid cells matched with ERA5.")
else:
    print("\nWARNING: Some rows are missing.")


# --------------------------------------------------
# Check missing values
# --------------------------------------------------

print("\nMissing values:")

missing = merged.isna().sum()

print(
    missing[missing > 0]
)


# --------------------------------------------------
# Save
# --------------------------------------------------

merged.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved to:")
print(OUTPUT_FILE)