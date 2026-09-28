from pathlib import Path
from datetime import datetime, timedelta

# Folder containing GFS NetCDF files
GFS_DIR = Path("gfs_api_output")

# July 2024
year = 2024
month = 7

# Required forecast accumulations
forecast_hours = ["f006", "f012", "f018", "f024"]

required_files = []

# Generate all 31 × 4 = 124 expected filenames
start_date = datetime(year, month, 1)

for day in range(31):
    date = start_date + timedelta(days=day)

    date_str = date.strftime("%Y%m%d")

    for fh in forecast_hours:
        filename = f"gfs.0p25.{date_str}00.{fh}.grib2.nc"
        required_files.append(filename)


# Check files
found = []
missing = []

for filename in required_files:
    filepath = GFS_DIR / filename

    if filepath.exists():
        found.append(filename)
    else:
        missing.append(filename)


# Print result
print("=" * 50)
print("GFS JULY 2024 FILE CHECK")
print("=" * 50)

print(f"REQUIRED FILES: {len(required_files)}")
print(f"FOUND FILES:    {len(found)}")
print(f"MISSING FILES:  {len(missing)}")

if missing:
    print("\nMissing files:")
    for filename in missing:
        print(filename)
else:
    print("\n✅ ALL 124 GFS FILES ARE PRESENT!")

print("=" * 50)