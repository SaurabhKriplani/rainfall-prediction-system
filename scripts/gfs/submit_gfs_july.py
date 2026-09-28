from pathlib import Path
import subprocess
import re
from datetime import datetime, timedelta

CONTROL_DIR = Path("gfs_controls")
CONTROL_DIR.mkdir(exist_ok=True)

REQUEST_LOG = Path("gfs_requests.txt")

START_DATE = datetime(2024, 7, 1)
END_DATE = datetime(2024, 7, 31)

products = [
    "6-hour Accumulation (initial+0 to initial+6)",
    "6-hour Accumulation (initial+6 to initial+12)",
    "6-hour Accumulation (initial+12 to initial+18)",
    "6-hour Accumulation (initial+18 to initial+24)",
]

# Already completed:
completed = {
    ("20240701", 0): "928142"
}

with open(REQUEST_LOG, "w", encoding="utf-8") as log:

    # Save existing request
    log.write(
        "2024-07-01,0,928142,"
        "6-hour Accumulation (initial+0 to initial+6)\n"
    )

    current = START_DATE

    while current <= END_DATE:

        date_code = current.strftime("%Y%m%d")
        init_time = current.strftime("%Y%m%d0000")

        for i, product in enumerate(products):

            # Skip the request we already submitted
            if (date_code, i) in completed:
                continue

            control_file = (
                CONTROL_DIR /
                f"gfs_{date_code}_{i+1}.ctl"
            )

            content = f"""dataset=d084001
date={init_time}/to/{init_time}
datetype=init
param=A PCP
oformat=netCDF
nlat=38
slat=6
wlon=68
elon=98
product={product}
targetdir=./gfs_api_output
"""

            control_file.write_text(
                content,
                encoding="utf-8"
            )

            print()
            print("=" * 60)
            print(f"Date: {date_code}")
            print(f"Product: {i + 1}/4")
            print(product)
            print("=" * 60)

            result = subprocess.run(
                ["gdex_client", "-submit", str(control_file)],
                capture_output=True,
                text=True
            )

            print(result.stdout)

            match = re.search(
                r'"request_id":\s*"(\d+)"',
                result.stdout
            )

            if match:
                request_id = match.group(1)

                log.write(
                    f"{current:%Y-%m-%d},"
                    f"{i},"
                    f"{request_id},"
                    f"{product}\n"
                )

                log.flush()

                print(f"REQUEST ID = {request_id}")

            else:
                print("WARNING: Request ID not found.")
                print(result.stderr)

        current += timedelta(days=1)

print()
print("=" * 60)
print("ALL REQUESTS SUBMITTED")
print(f"Request log: {REQUEST_LOG}")
print("=" * 60)