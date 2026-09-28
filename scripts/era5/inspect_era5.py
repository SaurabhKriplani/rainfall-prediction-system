import xarray as xr

ds = xr.open_dataset("era5_test.nc")

print("\n========== DATASET ==========")
print(ds)

print("\n========== VARIABLES ==========")
for var in ds.data_vars:
    print(var)

print("\n========== DIMENSIONS ==========")
for name, size in ds.sizes.items():
    print(name, "=", size)

print("\n========== TIME ==========")
print(ds.valid_time.values)

print("\n========== PRESSURE LEVELS ==========")
print(ds.pressure_level.values)

print("\n========== LATITUDE ==========")
print(ds.latitude.values)

print("\n========== LONGITUDE ==========")
print(ds.longitude.values)