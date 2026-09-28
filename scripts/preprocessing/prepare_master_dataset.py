import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# PATHS
# ============================================================

ROOT = Path.cwd()

GFS_FILE = ROOT / "data" / "final" / "gfs_24h_jul_sep_2024.csv"

IMD_FILE = ROOT / "data" / "imd" / "RF25_ind2024_rfp25 (1).nc"

ERA5_FILES = [
    ROOT / "data" / "era5" / "test" / "era5_test.nc",
    ROOT / "data" / "era5" / "era5_08_2024.nc",
    ROOT / "data" / "era5" / "era5_09_2024.nc",
]

OUTPUT_DIR = ROOT / "data" / "final"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMD_OUTPUT = OUTPUT_DIR / "imd_jul_sep_2024.csv"
ERA5_OUTPUT = OUTPUT_DIR / "era5_jul_sep_2024.csv"
MASTER_OUTPUT = OUTPUT_DIR / "master_jul_sep_2024.csv"

START_DATE = pd.Timestamp("2024-07-01")
END_DATE = pd.Timestamp("2024-09-30")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_var(ds, names):

    for name in names:
        if name in ds.data_vars:
            return name

    lower = {x.lower(): x for x in ds.data_vars}

    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]

    return None


def find_coord(ds, names):

    for name in names:
        if name in ds.coords:
            return name

    for actual in list(ds.coords) + list(ds.dims):
        for name in names:
            if actual.lower() == name.lower():
                return actual

    return None


# ============================================================
# 1. LOAD COMPLETED GFS DATA
# ============================================================

print("\n" + "=" * 70)
print("1. LOADING COMPLETED GFS DATA")
print("=" * 70)

if not GFS_FILE.exists():
    raise FileNotFoundError(
        f"GFS file not found:\n{GFS_FILE}"
    )

gfs = pd.read_csv(GFS_FILE)

gfs["date"] = pd.to_datetime(gfs["date"])

print("GFS shape:", gfs.shape)

print(
    "GFS dates:",
    gfs["date"].min(),
    "→",
    gfs["date"].max()
)

print(
    "GFS grid:",
    gfs["latitude"].nunique(),
    "x",
    gfs["longitude"].nunique()
)

# Only required period
gfs = gfs[
    (gfs["date"] >= START_DATE) &
    (gfs["date"] <= END_DATE)
].copy()

print(
    "GFS after date filtering:",
    gfs.shape
)


# ============================================================
# 2. PROCESS IMD
# ============================================================

print("\n" + "=" * 70)
print("2. PROCESSING IMD")
print("=" * 70)

if not IMD_FILE.exists():
    raise FileNotFoundError(
        f"IMD file not found:\n{IMD_FILE}"
    )

print("IMD file:")
print(IMD_FILE)

ds = xr.open_dataset(IMD_FILE)

print(
    "IMD dimensions:",
    dict(ds.dims)
)

rain_var = find_var(
    ds,
    ["RAINFALL", "rainfall", "RF"]
)

time_name = find_coord(
    ds,
    ["TIME", "time"]
)

lat_name = find_coord(
    ds,
    ["LATITUDE", "latitude", "lat"]
)

lon_name = find_coord(
    ds,
    ["LONGITUDE", "longitude", "lon"]
)

if rain_var is None:
    raise ValueError(
        "IMD rainfall variable not found."
    )

print("Rainfall variable:", rain_var)
print("Time:", time_name)
print("Latitude:", lat_name)
print("Longitude:", lon_name)


# ------------------------------------------------------------
# Select July-September
# ------------------------------------------------------------

rainfall = ds[rain_var].sel(
    {
        time_name: slice(
            START_DATE,
            END_DATE
        )
    }
)

rainfall = rainfall.rename({
    time_name: "date",
    lat_name: "latitude",
    lon_name: "longitude"
})

rainfall = rainfall.sortby("latitude")
rainfall = rainfall.sortby("longitude")

print(
    "IMD dates:",
    rainfall.date.values[0],
    "→",
    rainfall.date.values[-1]
)


# ------------------------------------------------------------
# Determine common GFS/IMD spatial region
# ------------------------------------------------------------

gfs_lat_min = float(gfs["latitude"].min())
gfs_lat_max = float(gfs["latitude"].max())

gfs_lon_min = float(gfs["longitude"].min())
gfs_lon_max = float(gfs["longitude"].max())

imd_lat_min = float(rainfall.latitude.min())
imd_lat_max = float(rainfall.latitude.max())

imd_lon_min = float(rainfall.longitude.min())
imd_lon_max = float(rainfall.longitude.max())

common_lat_min = max(
    gfs_lat_min,
    imd_lat_min
)

common_lat_max = min(
    gfs_lat_max,
    imd_lat_max
)

common_lon_min = max(
    gfs_lon_min,
    imd_lon_min
)

common_lon_max = min(
    gfs_lon_max,
    imd_lon_max
)

print("\nCommon spatial region:")
print(
    f"Latitude: {common_lat_min} → {common_lat_max}"
)
print(
    f"Longitude: {common_lon_min} → {common_lon_max}"
)


# ------------------------------------------------------------
# Get GFS target grid
# ------------------------------------------------------------

target_lats = np.sort(
    gfs.loc[
        (gfs["latitude"] >= common_lat_min) &
        (gfs["latitude"] <= common_lat_max),
        "latitude"
    ].unique()
)

target_lons = np.sort(
    gfs.loc[
        (gfs["longitude"] >= common_lon_min) &
        (gfs["longitude"] <= common_lon_max),
        "longitude"
    ].unique()
)

print(
    "Target grid:",
    len(target_lats),
    "x",
    len(target_lons)
)


# ------------------------------------------------------------
# Interpolate IMD onto GFS grid
# ------------------------------------------------------------

print("\nInterpolating IMD onto GFS grid...")

imd_interp = rainfall.interp(
    latitude=xr.DataArray(
        target_lats,
        dims="latitude"
    ),
    longitude=xr.DataArray(
        target_lons,
        dims="longitude"
    ),
    method="linear"
)

imd = imd_interp.to_dataframe(
    name="imd_rainfall"
).reset_index()

imd["date"] = pd.to_datetime(
    imd["date"]
)

imd["imd_rainfall"] = pd.to_numeric(
    imd["imd_rainfall"],
    errors="coerce"
)

imd["imd_rainfall"] = (
    imd["imd_rainfall"]
    .clip(lower=0)
)

ds.close()

imd.to_csv(
    IMD_OUTPUT,
    index=False
)

print(
    "IMD processed shape:",
    imd.shape
)

print(
    "Saved:",
    IMD_OUTPUT
)


# ============================================================
# 3. PROCESS ERA5
# ============================================================

print("\n" + "=" * 70)
print("3. PROCESSING ERA5")
print("=" * 70)

for file in ERA5_FILES:

    if not file.exists():
        raise FileNotFoundError(
            f"ERA5 file not found:\n{file}"
        )

print("ERA5 files:")

for file in ERA5_FILES:
    print(" ", file)


era5_parts = []


# ------------------------------------------------------------
# Process each ERA5 file
# ------------------------------------------------------------

for file in ERA5_FILES:

    print(
        "\nProcessing:",
        file.name
    )

    ds = xr.open_dataset(file)

    time_name = find_coord(
        ds,
        ["valid_time", "time"]
    )

    if time_name != "time":

        ds = ds.rename({
            time_name: "time"
        })

    ds = ds.sel(
        time=slice(
            START_DATE,
            END_DATE
        )
    )

    lat_name = find_coord(
        ds,
        ["latitude", "lat"]
    )

    lon_name = find_coord(
        ds,
        ["longitude", "lon"]
    )

    if lat_name != "latitude":

        ds = ds.rename({
            lat_name: "latitude"
        })

    if lon_name != "longitude":

        ds = ds.rename({
            lon_name: "longitude"
        })

    print(
        "Time points:",
        len(ds.time)
    )

    # --------------------------------------------------------
    # Your ERA5 files have:
    #
    # 00 UTC
    # 06 UTC
    # 12 UTC
    # 18 UTC
    #
    # Convert these into one daily mean.
    # --------------------------------------------------------

    ds = ds.resample(
        time="1D"
    ).mean()

    era5_parts.append(ds)


# ------------------------------------------------------------
# Combine July + August + September
# ------------------------------------------------------------

era5 = xr.concat(
    era5_parts,
    dim="time"
)


# Remove duplicate dates
_, unique_indices = np.unique(
    era5.time.values,
    return_index=True
)

era5 = era5.isel(
    time=np.sort(unique_indices)
)

era5 = era5.sortby("latitude")
era5 = era5.sortby("longitude")


print(
    "\nERA5 combined dates:",
    era5.time.values[0],
    "→",
    era5.time.values[-1]
)

print(
    "ERA5 unique days:",
    len(era5.time)
)


# ------------------------------------------------------------
# Restrict ERA5 to common spatial region
# ------------------------------------------------------------

era5 = era5.sel(
    latitude=slice(
        common_lat_min,
        common_lat_max
    ),
    longitude=slice(
        common_lon_min,
        common_lon_max
    )
)


# ------------------------------------------------------------
# Interpolate ERA5 onto GFS grid
# ------------------------------------------------------------

print(
    "\nInterpolating ERA5 onto GFS grid..."
)

era5 = era5.interp(
    latitude=xr.DataArray(
        target_lats,
        dims="latitude"
    ),
    longitude=xr.DataArray(
        target_lons,
        dims="longitude"
    ),
    method="linear"
)


# ------------------------------------------------------------
# Convert ERA5 to DataFrame
# ------------------------------------------------------------

era5_df = era5.to_dataframe().reset_index()

era5_df = era5_df.rename(
    columns={
        "time": "date"
    }
)

era5_df["date"] = pd.to_datetime(
    era5_df["date"]
)


# ============================================================
# 4. CONVERT PRESSURE LEVELS INTO COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("4. FORMATTING ERA5 FEATURES")
print("=" * 70)

variables = [
    "z",
    "r",
    "t",
    "u",
    "v",
    "w"
]

existing_variables = [
    x for x in variables
    if x in era5_df.columns
]

print(
    "ERA5 variables:",
    existing_variables
)

era5_df = era5_df.pivot_table(
    index=[
        "date",
        "latitude",
        "longitude"
    ],
    columns="pressure_level",
    values=existing_variables
).reset_index()


# ------------------------------------------------------------
# Flatten MultiIndex columns
# ------------------------------------------------------------

new_columns = []

for column in era5_df.columns:

    if isinstance(column, tuple):

        variable = column[0]
        level = column[1]

        if variable in existing_variables:

            new_columns.append(
                f"{variable}{int(level)}"
            )

        else:

            new_columns.append(
                str(variable)
            )

    else:

        new_columns.append(
            str(column)
        )

era5_df.columns = new_columns


era5_df.to_csv(
    ERA5_OUTPUT,
    index=False
)

print(
    "ERA5 processed shape:",
    era5_df.shape
)

print(
    "ERA5 dates:",
    era5_df["date"].min(),
    "→",
    era5_df["date"].max()
)

print(
    "Saved:",
    ERA5_OUTPUT
)


# ============================================================
# 5. MERGE GFS + IMD
# ============================================================

print("\n" + "=" * 70)
print("5. MERGING GFS + IMD")
print("=" * 70)

# Keep GFS only on common grid
gfs = gfs[
    gfs["latitude"].isin(target_lats)
    &
    gfs["longitude"].isin(target_lons)
].copy()

master = pd.merge(
    gfs,
    imd,
    on=[
        "date",
        "latitude",
        "longitude"
    ],
    how="inner"
)

print(
    "GFS + IMD shape:",
    master.shape
)


# ============================================================
# 6. MERGE ERA5
# ============================================================

print("\n" + "=" * 70)
print("6. MERGING ERA5")
print("=" * 70)

master = pd.merge(
    master,
    era5_df,
    on=[
        "date",
        "latitude",
        "longitude"
    ],
    how="inner"
)

print(
    "Final merged shape:",
    master.shape
)


# ============================================================
# 7. CREATE BIAS
# ============================================================

print("\n" + "=" * 70)
print("7. CREATING GFS BIAS")
print("=" * 70)

master["bias"] = (
    master["imd_rainfall"]
    -
    master["gfs_rain_24h"]
)


# ============================================================
# 8. SORT
# ============================================================

master = master.sort_values(
    [
        "date",
        "latitude",
        "longitude"
    ]
).reset_index(drop=True)


# ============================================================
# 9. VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("8. FINAL VALIDATION")
print("=" * 70)

print(
    "\nFinal shape:",
    master.shape
)

print(
    "Date range:",
    master["date"].min(),
    "→",
    master["date"].max()
)

print(
    "Unique dates:",
    master["date"].nunique()
)

print(
    "Unique latitude:",
    master["latitude"].nunique()
)

print(
    "Unique longitude:",
    master["longitude"].nunique()
)

print("\nColumns:")

print(
    master.columns.tolist()
)

print("\nMissing values:")

print(
    master.isna().sum()
)

print("\nRainfall statistics:")

print(
    master[
        [
            "gfs_rain_24h",
            "imd_rainfall",
            "bias"
        ]
    ].describe()
)


# ============================================================
# 10. SAVE MASTER DATASET
# ============================================================

master.to_csv(
    MASTER_OUTPUT,
    index=False
)

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)

print(
    "\nMaster dataset:"
)

print(
    MASTER_OUTPUT
)

print(
    "\nExpected period:"
)

print(
    "2024-07-01 → 2024-09-30"
)



# ============================================================
# CREATE ML TRAINING DATASET
# ============================================================

print("\n" + "=" * 70)
print("9. CREATING ML TRAINING DATASET")
print("=" * 70)

training = master.dropna(
    subset=[
        "imd_rainfall",
        "bias"
    ]
).copy()

TRAINING_OUTPUT = (
    OUTPUT_DIR /
    "master_training_jul_sep_2024.csv"
)

training.to_csv(
    TRAINING_OUTPUT,
    index=False
)

print(
    "Total master rows:",
    len(master)
)

print(
    "Valid observed rainfall rows:",
    len(training)
)

print(
    "Removed rows:",
    len(master) - len(training)
)

print(
    "Training dates:",
    training["date"].min(),
    "→",
    training["date"].max()
)

print(
    "Training unique dates:",
    training["date"].nunique()
)

print(
    "\nSaved training dataset:"
)

print(
    TRAINING_OUTPUT
)