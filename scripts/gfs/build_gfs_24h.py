from pathlib import Path
import xarray as xr
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GFS_DIR = PROJECT_ROOT / "data" / "gfs" / "july_2024" / "gfs_api_output"

OUTPUT_DIR = PROJECT_ROOT / "data" / "gfs"

OUTPUT_CSV = OUTPUT_DIR / "gfs_24h_july_2024.csv"


print("PROJECT ROOT:", PROJECT_ROOT)
print("GFS DIRECTORY:", GFS_DIR)
print("GFS FILE COUNT:", len(list(GFS_DIR.glob("*.grib2.nc"))))

# ============================================================
# SETTINGS
# ============================================================

YEAR = 2024
MONTH = 7

FORECAST_HOURS = [6, 12, 18, 24]


# ============================================================
# FIND PRECIPITATION VARIABLE
# ============================================================

def find_precip_variable(ds):

    # GDEX/NCEP GFS precipitation variable
    if "A_PCP_L1_Accum_1" in ds.data_vars:
        return "A_PCP_L1_Accum_1"

    # Fallback for other possible NetCDF variable names
    precip_vars = [
        v for v in ds.data_vars
        if "precip" in v.lower()
    ]

    if not precip_vars:
        raise RuntimeError(
            "No precipitation variable found.\n"
            f"Available variables: {list(ds.data_vars)}"
        )

    return precip_vars[0]


# ============================================================
# PROCESS ONE DAY
# ============================================================

def process_day(date_str):

    print("\n" + "=" * 60)
    print(f"PROCESSING {date_str}")
    print("=" * 60)

    rainfall = []

    for forecast_hour in FORECAST_HOURS:

        fh = f"{forecast_hour:03d}"

        filename = (
            f"gfs.0p25.{date_str}00."
            f"f{fh}.grib2.nc"
        )

        filepath = GFS_DIR / filename

        print(f"\nOpening: {filename}")

        if not filepath.exists():
            raise FileNotFoundError(
                f"Missing file:\n{filepath}"
            )

        ds = xr.open_dataset(filepath)

        print("Variables:")
        print(list(ds.data_vars))

        precip_name = find_precip_variable(ds)

        print("Using:", precip_name)

        rain = ds[precip_name].squeeze()

        # Load before closing dataset
        rain = rain.load()

        print(
            "Min:",
            float(rain.min())
        )

        print(
            "Max:",
            float(rain.max())
        )

        # Load data into memory before closing dataset
        rain = rain.load()

        rainfall.append(rain)

        ds.close()

    # ========================================================
    # SUM FOUR 6-HOUR ACCUMULATIONS
    # ========================================================

    print("\nCalculating 24-hour rainfall...")

    gfs_rain_24h = (
        rainfall[0]
        + rainfall[1]
        + rainfall[2]
        + rainfall[3]
    )

    print(
        "Minimum:",
        float(gfs_rain_24h.min())
    )

    print(
        "Maximum:",
        float(gfs_rain_24h.max())
    )

    print(
        "Mean:",
        float(gfs_rain_24h.mean())
    )

    # ========================================================
    # CONVERT TO DATAFRAME
    # ========================================================

    df = gfs_rain_24h.to_dataframe(
        name="gfs_rain_24h"
    ).reset_index()


    df = df.rename(
        columns={
            "lat": "latitude",
            "lon": "longitude"
        }
    )


    # Add date
    df["date"] = pd.to_datetime(
        date_str,
        format="%Y%m%d"
    )

    # Keep only useful columns
    df = df[
        [
            "date",
            "latitude",
            "longitude",
            "gfs_rain_24h"
        ]
    ]

    return df


# ============================================================
# PROCESS ALL 31 DAYS
# ============================================================

def main():

    print("=" * 60)
    print("BUILDING GFS JULY 2024 24-HOUR DATASET")
    print("=" * 60)

    print("GFS directory:")
    print(GFS_DIR)

    all_days = []

    for day in range(1, 32):

        date_str = (
            f"{YEAR}"
            f"{MONTH:02d}"
            f"{day:02d}"
        )

        df = process_day(date_str)

        print(
            f"\nGrid rows for {date_str}: "
            f"{len(df):,}"
        )

        all_days.append(df)

    # ========================================================
    # COMBINE ALL DAYS
    # ========================================================

    print("\n" + "=" * 60)
    print("COMBINING ALL DAYS")
    print("=" * 60)

    final_df = pd.concat(
        all_days,
        ignore_index=True
    )

    # Sort
    final_df = final_df.sort_values(
        [
            "date",
            "latitude",
            "longitude"
        ]
    )

    # ========================================================
    # SAVE CSV
    # ========================================================

    final_df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    # ========================================================
    # FINAL INFORMATION
    # ========================================================

    print("\n" + "=" * 60)
    print("GFS 24-HOUR DATASET COMPLETE")
    print("=" * 60)

    print(
        "Rows:",
        f"{len(final_df):,}"
    )

    print(
        "Columns:",
        list(final_df.columns)
    )

    print(
        "Date range:",
        final_df["date"].min(),
        "→",
        final_df["date"].max()
    )

    print(
        "Output:",
        OUTPUT_CSV
    )

    print("\nFirst 10 rows:")
    print(final_df.head(10))

    print("\nLast 10 rows:")
    print(final_df.tail(10))

    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()