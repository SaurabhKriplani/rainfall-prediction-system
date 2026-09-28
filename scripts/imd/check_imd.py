import xarray as xr
import numpy as np

ds = xr.open_dataset("data/imd/imd_july_2024.nc")

rain = ds["RAINFALL"]

# Valid spatial mask using July 1
mask = ~np.isnan(rain.isel(TIME=0))

lat = ds["LATITUDE"].values
lon = ds["LONGITUDE"].values

valid_lat = lat[np.any(mask.values, axis=1)]
valid_lon = lon[np.any(mask.values, axis=0)]

print("Valid latitude range:")
print(valid_lat.min(), "to", valid_lat.max())

print("\nValid longitude range:")
print(valid_lon.min(), "to", valid_lon.max())

print("\nNumber of valid latitude rows:", len(valid_lat))
print("Number of valid longitude columns:", len(valid_lon))

print("\nValid cells on July 1:", int(mask.sum()))