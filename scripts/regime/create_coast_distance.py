import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# ============================================================
# PATHS
# ============================================================

COASTLINE_FILE = (
    "data/geography/coastline/"
    "ne_10m_coastline.shp"
)

ELEVATION_FILE = (
    "data/geography/dem/"
    "gfs_elevation_features.csv"
)

OUTPUT_FILE = (
    "data/geography/"
    "gfs_geographic_features.csv"
)


# ============================================================
# LOAD GFS GRID
# ============================================================

print("Loading GFS grid...")

df = pd.read_csv(ELEVATION_FILE)

print(
    f"GFS grid cells: {len(df)}"
)


# ============================================================
# CREATE POINT GEOMETRIES
# ============================================================

points = gpd.GeoDataFrame(
    df,
    geometry=[
        Point(lon, lat)
        for lon, lat in zip(
            df["longitude"],
            df["latitude"]
        )
    ],
    crs="EPSG:4326"
)


# ============================================================
# LOAD NATURAL EARTH COASTLINE
# ============================================================

print("Loading Natural Earth coastline...")

coast = gpd.read_file(
    COASTLINE_FILE
)

print(
    f"Coastline features: {len(coast)}"
)

print(
    f"Coastline CRS: {coast.crs}"
)


# ============================================================
# MAKE SURE COASTLINE IS WGS84
# ============================================================

if coast.crs is None:
    raise ValueError(
        "Coastline has no CRS information."
    )

coast = coast.to_crs("EPSG:4326")


# ============================================================
# UTM ZONE FUNCTION
# ============================================================

def get_utm_zone(longitude):

    return int(
        (longitude + 180) // 6
    ) + 1


# ============================================================
# CALCULATE DISTANCE BY UTM ZONE
# ============================================================

print()
print("Calculating coast distances...")


points["utm_zone"] = (
    points["longitude"]
    .apply(get_utm_zone)
)


all_results = []


for zone, group in points.groupby(
    "utm_zone"
):

    print(
        f"Processing UTM zone {zone} "
        f"({len(group)} grid cells)..."
    )


    # --------------------------------------------------------
    # Northern hemisphere UTM EPSG
    # --------------------------------------------------------

    epsg = 32600 + int(zone)

    print(
        f"Using EPSG:{epsg}"
    )


    # --------------------------------------------------------
    # Project GFS points
    # --------------------------------------------------------

    group_projected = group.to_crs(
        epsg=epsg
    )


    # --------------------------------------------------------
    # Project coastline
    # --------------------------------------------------------

    coast_projected = coast.to_crs(
        epsg=epsg
    )


    # --------------------------------------------------------
    # Nearest coastline
    # --------------------------------------------------------

    joined = gpd.sjoin_nearest(
        group_projected,
        coast_projected,
        how="left",
        distance_col="coast_distance_m"
    )


    # --------------------------------------------------------
    # Remove duplicate matches
    # --------------------------------------------------------

    joined = (
        joined
        .sort_values(
            "coast_distance_m"
        )
        .drop_duplicates(
            subset=[
                "latitude",
                "longitude"
            ],
            keep="first"
        )
    )


    # --------------------------------------------------------
    # Convert metres → kilometres
    # --------------------------------------------------------

    joined["coast_distance_km"] = (
        joined["coast_distance_m"] / 1000.0
    )


    # --------------------------------------------------------
    # Keep required columns
    # --------------------------------------------------------

    result = joined[
        [
            "latitude",
            "longitude",
            "elevation_m",
            "coast_distance_km"
        ]
    ].copy()


    all_results.append(
        result
    )


# ============================================================
# COMBINE RESULTS
# ============================================================

result = pd.concat(
    all_results,
    ignore_index=True
)


# ============================================================
# SORT
# ============================================================

result = result.sort_values(
    [
        "latitude",
        "longitude"
    ]
).reset_index(
    drop=True
)


# ============================================================
# CHECK DUPLICATES
# ============================================================

duplicates = result.duplicated(
    subset=[
        "latitude",
        "longitude"
    ]
).sum()

print()
print(
    f"Duplicate grid cells: {duplicates}"
)


# ============================================================
# CHECK MISSING
# ============================================================

print()
print("Missing values:")

print(
    result[
        [
            "elevation_m",
            "coast_distance_km"
        ]
    ]
    .isna()
    .sum()
)


# ============================================================
# STATISTICS
# ============================================================

print()
print("=" * 60)

print(
    "Coast distance statistics:"
)

print(
    result[
        "coast_distance_km"
    ].describe()
)


print("=" * 60)


# ============================================================
# SAVE
# ============================================================

result.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print(
    f"Saved geographic features to:"
)

print(
    OUTPUT_FILE
)

print(
    f"Rows: {len(result)}"
)

print("=" * 60)