import xarray as xr
import glob
import os

files = sorted(
    glob.glob("gfs_24h_test/gfs_f*.nc")
)

for file in files:

    print("\n" + "=" * 60)
    print(os.path.basename(file))
    print("=" * 60)

    ds = xr.open_dataset(file)

    print("Reference time:")
    print(ds["reftime"].values)

    # Find time coordinate
    time_coords = [
        c for c in ds.coords
        if "time" in c.lower()
    ]

    print("\nTime coordinates:")
    print(time_coords)

    for coord in time_coords:
        print(f"\n{coord}:")
        print(ds[coord].values)

    # Find bounds variable
    bounds_vars = [
        v for v in ds.data_vars
        if "bounds" in v.lower()
    ]

    print("\nTime bounds:")

    for v in bounds_vars:
        print(v)
        print(ds[v].values)

    # Find precipitation variable
    precip_vars = [
        v for v in ds.data_vars
        if "precip" in v.lower()
    ]

    for v in precip_vars:

        print("\nPrecipitation variable:")
        print(v)

        print("\nAttributes:")
        print(ds[v].attrs)