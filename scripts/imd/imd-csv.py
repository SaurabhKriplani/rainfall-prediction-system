import xarray as xr
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMD_FILE = PROJECT_ROOT / "data" / "imd" / "imd_july_2024.nc"
OUTPUT_FILE = PROJECT_ROOT / "data" / "imd" / "imd_july_2024.csv"

# Load IMD
ds = xr.open_dataset(IMD_FILE)

rain = ds["RAINFALL"]

# Convert to dataframe
df = rain.to_dataframe(
    name="imd_rainfall"
).reset_index()

# Remove invalid IMD cells
df = df.dropna(subset=["imd_rainfall"])

# Rename coordinates
df = df.rename(columns={
    "TIME": "date",
    "LATITUDE": "latitude",
    "LONGITUDE": "longitude"
})

# Normalize date
df["date"] = pd.to_datetime(df["date"])

# Normalize coordinates
df["latitude"] = df["latitude"].round(2)
df["longitude"] = df["longitude"].round(2)

# Save
df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("IMD CSV created successfully.")
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())

print("\nDate range:")
print(df["date"].min(), "to", df["date"].max())

print("\nUnique dates:", df["date"].nunique())
print("Unique coordinates:", df[["latitude", "longitude"]].drop_duplicates().shape[0])

print("\nRainfall statistics:")
print(df["imd_rainfall"].describe())

print("\nSaved to:")
print(OUTPUT_FILE)