import os
import glob
import numpy as np
import pandas as pd
import rasterio
from rasterio.merge import merge
from rasterio.windows import Window


# ============================================================
# PATHS
# ============================================================

TILE_DIR = "data/geography/dem/tiles"

OUTPUT_DIR = "data/geography/dem"

GFS_FILE = "data/gfs/gfs_24h_july_2024.csv"

OUTPUT_DEM = os.path.join(
    OUTPUT_DIR,
    "dem_mosaic.tif"
)

OUTPUT_FEATURES = os.path.join(
    OUTPUT_DIR,
    "gfs_elevation_features.csv"
)


# ============================================================
# LOAD DEM TILES
# ============================================================

tiles = sorted(
    glob.glob(
        os.path.join(TILE_DIR, "dem_*.tif")
    )
)

print(f"Found {len(tiles)} DEM tiles.")

if len(tiles) != 42:
    raise ValueError(
        f"Expected 42 DEM tiles, found {len(tiles)}"
    )


src_files = [
    rasterio.open(tile)
    for tile in tiles
]


# ============================================================
# MERGE DEM
# ============================================================

print("Merging DEM tiles...")

mosaic, transform = merge(src_files)

profile = src_files[0].profile.copy()

profile.update(
    {
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": transform,
        "count": 1,
        "dtype": "float32"
    }
)


with rasterio.open(
    OUTPUT_DEM,
    "w",
    **profile
) as dst:

    dst.write(
        mosaic[0].astype("float32"),
        1
    )


print(
    f"Merged DEM saved to:\n{OUTPUT_DEM}"
)


# ============================================================
# CLOSE FILES
# ============================================================

for src in src_files:
    src.close()


# ============================================================
# LOAD GFS GRID
# ============================================================

print("Loading GFS grid...")

gfs = pd.read_csv(GFS_FILE)

gfs_coords = (
    gfs[
        ["latitude", "longitude"]
    ]
    .drop_duplicates()
    .sort_values(
        ["latitude", "longitude"]
    )
    .reset_index(drop=True)
)

print(
    f"GFS unique grid cells: {len(gfs_coords)}"
)


# ============================================================
# OPEN MERGED DEM
# ============================================================
with rasterio.open(OUTPUT_DEM) as dem:

    elevation_values = []

    for _, row in gfs_coords.iterrows():

        lat = row["latitude"]
        lon = row["longitude"]

        try:
            r, c = dem.index(lon, lat)

            # Clamp to nearest valid raster pixel
            r = max(0, min(r, dem.height - 1))
            c = max(0, min(c, dem.width - 1))

            elevation = dem.read(
                1,
                window=Window(
                    c,
                    r,
                    1,
                    1
                )
            )[0, 0]

            elevation_values.append(elevation)

        except Exception:
            elevation_values.append(np.nan)

# ============================================================
# CREATE ELEVATION DATAFRAME
# ============================================================

elevation_df = gfs_coords.copy()

elevation_df[
    "elevation_m"
] = elevation_values


# ============================================================
# BASIC CHECKS
# ============================================================

print()
print("=" * 60)

print(
    "Elevation statistics:"
)

print(
    elevation_df[
        "elevation_m"
    ].describe()
)


print()

print(
    "Missing elevation:",
    elevation_df[
        "elevation_m"
    ].isna().sum()
)


# ============================================================
# SAVE
# ============================================================

elevation_df.to_csv(
    OUTPUT_FEATURES,
    index=False
)


print()
print("=" * 60)

print(
    f"Elevation features saved:\n"
    f"{OUTPUT_FEATURES}"
)

print(
    f"Rows: {len(elevation_df)}"
)

print("=" * 60)