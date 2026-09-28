import cdsapi
from pathlib import Path
import calendar

client = cdsapi.Client()

OUTPUT_DIR = Path("data/era5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

dataset = "reanalysis-era5-pressure-levels"

variables = [
    "geopotential",
    "relative_humidity",
    "temperature",
    "u_component_of_wind",
    "v_component_of_wind",
    "vertical_velocity"
]

pressure_levels = [
    "500",
    "700",
    "850"
]

times = [
    "00:00",
    "06:00",
    "12:00",
    "18:00"
]

# Download August and September
for month in [8, 9]:

    month_str = f"{month:02d}"
    num_days = calendar.monthrange(2024, month)[1]

    output_file = OUTPUT_DIR / f"era5_{month_str}_2024.nc"

    print("\n" + "=" * 60)
    print(f"ERA5 {calendar.month_name[month].upper()} 2024")
    print("=" * 60)

    if output_file.exists():
        print(f"Already exists: {output_file}")
        print("Skipping...")
        continue

    days = [
        f"{d:02d}"
        for d in range(1, num_days + 1)
    ]

    request = {
        "product_type": ["reanalysis"],

        "variable": variables,

        "year": ["2024"],

        "month": [month_str],

        "day": days,

        "time": times,

        "pressure_level": pressure_levels,

        "data_format": "netcdf",

        "download_format": "unarchived",

        # North, West, South, East
        "area": [39, 66, 6, 101]
    }

    print(f"Period: 2024-{month_str}-01 → 2024-{month_str}-{num_days}")
    print("Variables: 6")
    print("Pressure levels: 500, 700, 850 hPa")
    print("Times: 00, 06, 12, 18 UTC")
    print("Area: 39N, 6N, 66E, 101E")
    print(f"Output: {output_file}")

    print("\nRequesting ERA5 data...")

    client.retrieve(
        dataset,
        request,
        str(output_file)
    )

    print("Download complete!")

print("\n" + "=" * 60)
print("AUGUST + SEPTEMBER ERA5 DOWNLOAD COMPLETE")
print("=" * 60)