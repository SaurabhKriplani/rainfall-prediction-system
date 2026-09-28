from pathlib import Path
import xarray as xr

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IMD_FILE = list(
    (PROJECT_ROOT / "data" / "imd").glob("*.nc")
)[0]

OUTPUT_FILE = (
    PROJECT_ROOT /
    "data" /
    "imd" /
    "imd_july_2024.nc"
)

# Open IMD data
ds = xr.open_dataset(IMD_FILE)

# Select July 2024
july = ds.sel(
    TIME=slice("2024-07-01", "2024-07-31")
)

print("Original dataset:")
print(ds)

print("\nJuly dataset:")
print(july)

print("\nJuly rainfall statistics:")
print(july["RAINFALL"].min().values)
print(july["RAINFALL"].max().values)
print(july["RAINFALL"].mean().values)

print("\nJuly dates:")
print(july.TIME.values)

# Save July only
july.to_netcdf(OUTPUT_FILE)

print("\nSaved:")
print(OUTPUT_FILE)