import subprocess
import time
import json
import re
from pathlib import Path
from datetime import date, timedelta


OUT_DIR = Path("gfs_api_output")
OUT_DIR.mkdir(exist_ok=True)

CONTROL_DIR = Path("gfs_controls")
CONTROL_DIR.mkdir(exist_ok=True)


# Already downloaded: July 1-3
SKIP = {
    ("2024-07-01", 6),
    ("2024-07-01", 12),
    ("2024-07-01", 18),
    ("2024-07-01", 24),

    ("2024-07-02", 6),
    ("2024-07-02", 12),
    ("2024-07-02", 18),
    ("2024-07-02", 24),

    ("2024-07-03", 6),
    ("2024-07-03", 12),
    ("2024-07-03", 18),
    ("2024-07-03", 24),
}


PRODUCTS = {
    6: "6-hour Accumulation (initial+0 to initial+6)",
    12: "6-hour Accumulation (initial+6 to initial+12)",
    18: "6-hour Accumulation (initial+12 to initial+18)",
    24: "6-hour Accumulation (initial+18 to initial+24)",
}


def run(cmd):
    print(">", " ".join(map(str, cmd)))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return result.returncode == 0


def make_control(day, fh):

    d = day.strftime("%Y%m%d")

    ctl = CONTROL_DIR / f"gfs_{d}_f{fh:03d}.ctl"

    text = f"""dataset=d084001
date={d}0000/to/{d}0000
datetype=init
param=A PCP
oformat=netCDF
nlat=38
slat=6
wlon=68
elon=98
product={PRODUCTS[fh]}
targetdir=./{OUT_DIR}
"""

    ctl.write_text(text)

    return ctl


def get_status():

    result = subprocess.run(
        ["gdex_client", "-get_status"],
        capture_output=True,
        text=True
    )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Could not parse GDEX status.")
        print(result.stdout)
        return None


# ==========================================
# BUILD MISSING REQUEST LIST
# ==========================================

jobs = []

day = date(2024, 7, 1)

while day <= date(2024, 7, 31):

    for fh in [6, 12, 18, 24]:

        key = (day.isoformat(), fh)

        if key not in SKIP:
            jobs.append((day, fh))

    day += timedelta(days=1)


print(f"\nTotal missing requests: {len(jobs)}")
print("Processing in batches of 6.\n")


# ==========================================
# PROCESS BATCHES
# ==========================================

for batch_start in range(0, len(jobs), 6):

    batch = jobs[batch_start:batch_start + 6]

    print("\n" + "=" * 60)
    print(
        f"BATCH {batch_start // 6 + 1} "
        f"({batch_start + 1}-{batch_start + len(batch)} "
        f"of {len(jobs)})"
    )
    print("=" * 60)

    request_ids = []


    # ======================================
    # SUBMIT
    # ======================================

    for day, fh in batch:

        ctl = make_control(day, fh)

        result = subprocess.run(
            ["gdex_client", "-submit", str(ctl)],
            capture_output=True,
            text=True
        )

        print(result.stdout)

        match = re.search(
            r'"request_id"\s*:\s*"(\d+)"',
            result.stdout
        )

        if match:

            request_id = match.group(1)

            request_ids.append(request_id)

            print(
                f"Submitted: "
                f"{day} f{fh:03d} -> {request_id}"
            )

        else:

            print(
                f"FAILED TO SUBMIT: "
                f"{day} f{fh:03d}"
            )


    if not request_ids:

        print("No requests submitted. Stopping.")

        break


    print("\nSubmitted request IDs:")
    print(request_ids)


    # ======================================
    # WAIT
    # ======================================

    print("\nWaiting for requests to complete...")


    while True:

        data = get_status()

        if data is None:
            time.sleep(30)
            continue

        if data.get("status") != "ok":

            print("GDEX status error.")
            print(data)

            time.sleep(30)
            continue


        statuses = {}

        for item in data.get("data", []):

            rid = str(item.get("request_index"))

            statuses[rid] = item.get("status")


        completed = 0
        errors = 0


        for rid in request_ids:

            status = statuses.get(rid, "Not found")

            print(f"{rid} -> {status}")

            if status == "Completed":
                completed += 1

            elif status == "Error":
                errors += 1


        if errors > 0:

            print(
                "\nERROR detected."
                "\nStopping WITHOUT purging."
                "\nCheck GDEX status before continuing."
            )

            raise SystemExit


        if completed == len(request_ids):

            print("\nALL REQUESTS COMPLETED.")

            break


        print(
            f"\nCompleted: "
            f"{completed}/{len(request_ids)}"
        )

        time.sleep(30)


    # ======================================
    # DOWNLOAD
    # ======================================

    print("\nDownloading completed files...")


    for rid in request_ids:

        success = run([
            "gdex_client",
            "-download",
            rid,
            "-outdir",
            str(OUT_DIR)
        ])

        if not success:

            print(
                f"DOWNLOAD FAILED for {rid}."
                "\nStopping before purge."
            )

            raise SystemExit


    # ======================================
    # PURGE
    # ======================================

    print("\nPurging completed requests...")


    for rid in request_ids:

        run([
            "gdex_client",
            "-purge",
            rid
        ])


    print("\nBATCH COMPLETE.")


print("\n" + "=" * 60)
print("JULY 4-31 DOWNLOAD COMPLETE")
print("=" * 60)