import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GFS_ERA5_FILE = (
    PROJECT_ROOT /
    "data" /
    "processed" /
    "gfs_era5_july_2024.csv"
)

IMD_FILE = (
    PROJECT_ROOT /
    "data" /
    "imd" /
    "imd_july_2024.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "gfs_era5_imd_july_2024.csv"


# --------------------------------------------------
# Load
# --------------------------------------------------

print("Loading GFS + ERA5...")
gfs_era5 = pd.read_csv(GFS_ERA5_FILE)

print("Loading IMD...")
imd = pd.read_csv(IMD_FILE)


# --------------------------------------------------
# Dates
# --------------------------------------------------

gfs_era5["date"] = pd.to_datetime(
    gfs_era5["date"],
    format="mixed"
)

imd["date"] = pd.to_datetime(
    imd["date"],
    format="mixed"
)


# --------------------------------------------------
# Coordinates
# --------------------------------------------------

for df in [gfs_era5, imd]:
    df["latitude"] = df["latitude"].round(2)
    df["longitude"] = df["longitude"].round(2)


# --------------------------------------------------
# Check duplicate keys
# --------------------------------------------------

key = ["date", "latitude", "longitude"]

print("\nGFS + ERA5 duplicate keys:")
print(gfs_era5.duplicated(key).sum())

print("\nIMD duplicate keys:")
print(imd.duplicated(key).sum())


# --------------------------------------------------
# Merge
# --------------------------------------------------

print("\nMerging...")

merged = pd.merge(
    gfs_era5,
    imd,
    on=key,
    how="inner",
    validate="one_to_one"
)


# --------------------------------------------------
# Results
# --------------------------------------------------

print("\n========== MERGE RESULT ==========")

print("GFS + ERA5 shape:", gfs_era5.shape)
print("IMD shape:", imd.shape)
print("Merged shape:", merged.shape)

print("\nColumns:")
print(merged.columns.tolist())

print("\nMissing values:")
print(merged.isna().sum()[merged.isna().sum() > 0])


# --------------------------------------------------
# Calculate bias
# --------------------------------------------------

merged["bias"] = (
    merged["imd_rainfall"] -
    merged["gfs_rain_24h"]
)


# --------------------------------------------------
# Bias statistics
# --------------------------------------------------

print("\n========== BIAS ==========")

print(merged["bias"].describe())


# --------------------------------------------------
# Save
# --------------------------------------------------

merged.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved to:")
print(OUTPUT_FILE)