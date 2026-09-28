import rasterio
import pandas as pd
import numpy as np
from rasterio.transform import rowcol

DEM = "data/geography/dem/dem_mosaic.tif"

GRID = "data/geography/dem/gfs_elevation_features.csv"

OUTPUT = "data/geography/gfs_terrain_features.csv"


# --------------------------------------------------
# Load GFS grid
# --------------------------------------------------

df = pd.read_csv(GRID)

print("GFS grid:", df.shape)


# --------------------------------------------------
# Open DEM
# --------------------------------------------------
with rasterio.open(DEM) as dem:

    elevation = dem.read(1).astype(float)

    if dem.nodata is not None:
        elevation[elevation == dem.nodata] = np.nan

    transform = dem.transform

    mean_lat = df["latitude"].mean()

    meters_per_degree_lat = 111320.0
    meters_per_degree_lon = (
        111320.0 * np.cos(np.radians(mean_lat))
    )

    pixel_x_m = abs(transform.a) * meters_per_degree_lon
    pixel_y_m = abs(transform.e) * meters_per_degree_lat

    print("DEM shape:", elevation.shape)

    print("Pixel size:")
    print("degrees:", abs(transform.a), abs(transform.e))
    print("metres:", pixel_x_m, pixel_y_m)

    # Calculate terrain slope correctly
    dz_dy, dz_dx = np.gradient(
        elevation,
        pixel_y_m,
        pixel_x_m
    )

    slope_radians = np.arctan(
        np.sqrt(dz_dx ** 2 + dz_dy ** 2)
    )

    slope_degrees = np.degrees(slope_radians)

    slopes = []

    for _, row in df.iterrows():

        lat = row["latitude"]
        lon = row["longitude"]

        r, c = dem.index(lon, lat)

        r = max(0, min(r, dem.height - 1))
        c = max(0, min(c, dem.width - 1))

        value = slope_degrees[r, c]

        slopes.append(value)
# --------------------------------------------------
# Save
# --------------------------------------------------

df["terrain_slope_deg"] = slopes

print("\nTerrain slope statistics:")
print(df["terrain_slope_deg"].describe())

print("\nMissing slope values:")
print(df["terrain_slope_deg"].isna().sum())

df.to_csv(OUTPUT, index=False)

print("\nSaved:")
print(OUTPUT)