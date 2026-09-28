import os
import sys
import json
import time
import shutil
import subprocess

from pathlib import Path
from datetime import date, timedelta


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GFS_ROOT = PROJECT_ROOT / "data" / "gfs"

CONTROL_ROOT = (
    GFS_ROOT
    / "gfs_controls"
)


# ============================================================
# DATE RANGE
# ============================================================

START_DATE = date(2024, 8, 1)
END_DATE = date(2024, 9, 30)


# ============================================================
# GDEX
# ============================================================

DATASET = "d084001"

# We only submit 6 at a time.
BATCH_SIZE = 6

CHECK_INTERVAL = 30


# ============================================================
# GDEX CLIENT
# ============================================================

VENV_GDEX = (
    Path(sys.executable).parent
    / "gdex_client.exe"
)

if VENV_GDEX.exists():
    GDEX_CLIENT = str(VENV_GDEX)
else:
    GDEX_CLIENT = "gdex_client"


# ============================================================
# GFS PRODUCTS
# ============================================================

PRODUCTS = {

    6:
        "6-hour Accumulation "
        "(initial+0 to initial+6)",

    12:
        "6-hour Accumulation "
        "(initial+6 to initial+12)",

    18:
        "6-hour Accumulation "
        "(initial+12 to initial+18)",

    24:
        "6-hour Accumulation "
        "(initial+18 to initial+24)",
}


FORECAST_HOURS = [
    6,
    12,
    18,
    24
]


# ============================================================
# SPATIAL SUBSET
# ============================================================

NLAT = 38
SLAT = 6
WLON = 68
ELON = 98


# ============================================================
# RUN GDEX
# ============================================================

def run_gdex(args):

    command = [
        GDEX_CLIENT
    ] + args

    print()
    print(
        "> "
        + " ".join(
            f'"{x}"'
            if " " in str(x)
            else str(x)
            for x in command
        )
    )

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return result


# ============================================================
# JSON PARSER
# ============================================================

def parse_json(text):

    text = text.strip()

    if not text:
        return None

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        start = text.find("{")
        end = text.rfind("}")

        if (
            start != -1
            and end != -1
            and end > start
        ):

            try:
                return json.loads(
                    text[start:end + 1]
                )

            except json.JSONDecodeError:
                return None

    return None


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

def get_output_dir(day):

    month = day.strftime(
        "%B"
    ).lower()

    directory = (
        GFS_ROOT
        / f"{month}_{day.year}"
        / "gfs_api_output"
    )

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return directory


# ============================================================
# CONTROL DIRECTORY
# ============================================================

def get_control_dir(day):

    month = day.strftime(
        "%B"
    ).lower()

    directory = (
        CONTROL_ROOT
        / f"{month}_{day.year}"
    )

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return directory


# ============================================================
# EXPECTED FILE
# ============================================================

def expected_filename(
    day,
    forecast_hour
):

    return (
        f"gfs.0p25."
        f"{day.strftime('%Y%m%d')}00."
        f"f{forecast_hour:03d}."
        f"grib2.nc"
    )


def expected_path(
    day,
    forecast_hour
):

    return (
        get_output_dir(day)
        / expected_filename(
            day,
            forecast_hour
        )
    )


# ============================================================
# FILE EXISTS
# ============================================================

def file_exists(
    day,
    forecast_hour
):

    path = expected_path(
        day,
        forecast_hour
    )

    return (
        path.exists()
        and path.stat().st_size > 0
    )


# ============================================================
# MALFORMED FILE REPAIR
# ============================================================

def repair_malformed_file(
    day,
    forecast_hour
):

    correct = expected_path(
        day,
        forecast_hour
    )

    if (
        correct.exists()
        and correct.stat().st_size > 0
    ):
        return True

    output_dir = get_output_dir(
        day
    )

    malformed = (
        output_dir.parent
        / (
            output_dir.name
            + expected_filename(
                day,
                forecast_hour
            )
        )
    )

    if (
        malformed.exists()
        and malformed.stat().st_size > 0
    ):

        print()
        print(
            "REPAIRING MALFORMED FILE"
        )

        print(
            f"From: {malformed}"
        )

        print(
            f"To:   {correct}"
        )

        shutil.move(
            str(malformed),
            str(correct)
        )

        return True

    return False


# ============================================================
# CREATE CONTROL FILE
# ============================================================

def make_control_file(
    day,
    forecast_hour
):

    directory = get_control_dir(
        day
    )

    date_string = day.strftime(
        "%Y%m%d"
    )

    control_file = (
        directory
        / (
            f"gfs_{date_string}"
            f"_f{forecast_hour:03d}.ctl"
        )
    )

    product = PRODUCTS[
        forecast_hour
    ]

    text = f"""dataset={DATASET}
date={date_string}0000/to/{date_string}0000
datetype=init
param=A PCP
product={product}
oformat=netCDF
nlat={NLAT}
slat={SLAT}
wlon={WLON}
elon={ELON}
"""

    control_file.write_text(
        text,
        encoding="utf-8"
    )

    return control_file


def submit_request(day, forecast_hour):

    control_file = make_control_file(
        day,
        forecast_hour
    )

    result = run_gdex([
        "-submit",
        str(control_file)
    ])

    if result.returncode != 0:

        print()
        print(
            "ERROR: GDEX submission command failed."
        )

        return None

    data = parse_json(
        result.stdout
    )

    if data is None:

        print()
        print(
            "ERROR: Could not parse GDEX response."
        )

        return None

    if data.get("status") != "ok":

        print()
        print(
            "ERROR: GDEX rejected the request."
        )

        print(data)

        return None

    request_data = data.get(
        "data",
        {}
    )

    request_id = str(
        request_data.get("request_id", "")
    )
    request_index = str(
        request_data.get("request_index") or request_id
    )

    if not request_index:

        print()
        print(
            "ERROR: No request ID/index returned."
        )

        print(data)

        return None

    print()
    print(
        f"Submitted: "
        f"{day.isoformat()} "
        f"f{forecast_hour:03d} "
        f"-> {request_id} ({request_index})"
    )

    return {
        "request_id": request_id,
        "request_index": request_index
    }


# ============================================================
# GET STATUS
# ============================================================

def get_status():

    result = run_gdex([
        "-get_status"
    ])

    data = parse_json(
        result.stdout
    )

    if data is None:
        return []

    if data.get("status") != "ok":
        return []

    return data.get(
        "data",
        []
    )


# ============================================================
# DATE FROM RINFO
# ============================================================

def request_matches_job(
    item,
    day,
    forecast_hour
):

    rinfo = item.get(
        "rinfo",
        ""
    )

    subset_info = item.get("subset_info")
    subset_note = (
        subset_info.get("note", "")
        if isinstance(subset_info, dict)
        else ""
    )

    expected_date = (
        day.strftime(
            "%Y-%m-%d"
        )
        + " 00:00"
    )
    expected_date_compact = day.strftime("%Y%m%d")

    date_matches = (
        f"startdate={expected_date}" in rinfo
        or expected_date_compact in subset_note
    )

    if not date_matches:
        return False

    product = PRODUCTS[
        forecast_hour
    ]

    product_matches = (
        f"product={product}" in rinfo
        or product in subset_note
    )

    if not product_matches:
        return False

    dsid = item.get("dsid", "")

    if (
        "dsnum=d084001" not in rinfo
        and dsid != "d084001"
    ):
        return False

    return True


# ============================================================
# DOWNLOAD REQUEST
# ============================================================

def download_request(
    request_id,
    day,
    forecast_hour
):

    expected = expected_path(
        day,
        forecast_hour
    )

    # Already downloaded
    if file_exists(
        day,
        forecast_hour
    ):

        print(
            f"Already exists: "
            f"{expected.name}"
        )

        return True

    output_dir = get_output_dir(
        day
    )

    # IMPORTANT:
    # trailing separator is required
    outdir = (
        str(output_dir)
        + os.sep
    )

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        result = run_gdex([
            "-download",
            str(request_id),
            "-outdir",
            outdir
        ])

        if file_exists(
            day,
            forecast_hour
        ):

            print(
                f"Verified: "
                f"{expected.name}"
            )

            return True

        # Try malformed path repair
        if repair_malformed_file(
            day,
            forecast_hour
        ):

            print(
                f"Verified after repair: "
                f"{expected.name}"
            )

            return True

        print(
            f"Download attempt {attempt}/{max_attempts} failed for "
            f"{request_id} ({expected.name})."
        )

        if attempt < max_attempts:
            print("Retrying in 10 seconds...")
            time.sleep(10)

    print()
    print(
        "Downloaded but expected "
        "file was not found or failed after retries:"
    )

    print(expected)

    return False


# ============================================================
# PURGE
# ============================================================

def purge_request(
    request_id
):

    print(
        f"Purging {request_id}"
    )

    result = run_gdex([
        "-purge",
        str(request_id)
    ])

    return (
        result.returncode == 0
    )


# ============================================================
# RECONCILE EXISTING GDEX REQUESTS
# ============================================================

def reconcile_existing_requests():

    print()
    print("=" * 70)
    print(
        "CHECKING EXISTING GDEX REQUESTS"
    )
    print("=" * 70)

    status_data = get_status()

    if not status_data:

        print(
            "No GDEX status data returned."
        )

        return

    for item in status_data:

        request_index = item.get("request_index") or item.get("request_id")

        if request_index is None:
            continue

        request_index = str(request_index)
        request_id = str(item.get("request_id") or request_index)

        status = item.get(
            "status",
            ""
        )

        rinfo = item.get(
            "rinfo",
            ""
        )

        dsid = item.get(
            "dsid",
            ""
        )

        # Only look at our GFS dataset
        if (
            "dsnum=d084001" not in rinfo
            and dsid != "d084001"
        ):
            continue

        # Skip already purged requests
        if status in {
            "Set for Purge",
            "Purged"
        }:
            continue

        # Purge errored/failed/cancelled requests to release server slots
        if status in {
            "Error",
            "Failed",
            "Cancelled"
        }:

            print(
                f"Purging failed/errored request "
                f"{request_id} ({request_index}) (status: {status})"
            )

            purge_request(request_index)

            continue

        matched_job = None

        current = START_DATE

        while current <= END_DATE:

            for fh in FORECAST_HOURS:

                if request_matches_job(
                    item,
                    current,
                    fh
                ):

                    matched_job = (
                        current,
                        fh
                    )

                    break

            if matched_job:
                break

            current += timedelta(
                days=1
            )

        if matched_job:

            day, fh = matched_job

            print()
            print(
                f"{request_id} ({request_index}) | "
                f"{day} | "
                f"f{fh:03d} | "
                f"{status}"
            )

            if status == "Completed":

                success = download_request(
                    request_index,
                    day,
                    fh
                )

                if success:

                    purge_request(
                        request_index
                    )

            else:

                print(
                    f"Request {request_id} "
                    f"is still processing."
                )

        else:

            # Non-Aug/Sep request (e.g. July) that completed
            if status == "Completed":

                print()
                print(
                    f"Purging completed non-Aug/Sep "
                    f"request {request_id} ({request_index})"
                )

                purge_request(
                    request_index
                )


# ============================================================
# BUILD JOBS
# ============================================================

def build_jobs():

    jobs = []

    current = START_DATE

    while current <= END_DATE:

        for fh in FORECAST_HOURS:

            jobs.append({
                "day": current,
                "forecast_hour": fh
            })

        current += timedelta(
            days=1
        )

    return jobs


# ============================================================
# FIND OPEN REQUEST COUNT
# ============================================================

def count_open_requests():

    status_data = get_status()

    return len(status_data)


# ============================================================
# WAIT UNTIL REQUEST SLOTS ARE AVAILABLE
# ============================================================

def wait_for_slots(
    needed_slots
):

    while True:

        reconcile_existing_requests()

        total_requests = count_open_requests()

        print()
        print(
            f"GDEX total requests on server: "
            f"{total_requests}"
        )

        if total_requests + needed_slots <= 10:

            return

        print(
            "GDEX request limit (10) reached."
        )

        print(
            "Waiting for existing "
            "requests to complete/purge..."
        )

        time.sleep(
            CHECK_INTERVAL
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "GFS AUGUST + SEPTEMBER 2024"
    )
    print("=" * 70)

    print(
        f"Dataset: {DATASET}"
    )

    print(
        f"Start: {START_DATE}"
    )

    print(
        f"End: {END_DATE}"
    )

    jobs = build_jobs()

    print(
        f"Expected files: "
        f"{len(jobs)}"
    )

    # --------------------------------------------------------
    # Repair/check local files
    # --------------------------------------------------------

    missing_jobs = []

    existing = 0

    for job in jobs:

        day = job["day"]
        fh = job["forecast_hour"]

        if file_exists(
            day,
            fh
        ):

            existing += 1

        elif repair_malformed_file(
            day,
            fh
        ):

            existing += 1

        else:

            missing_jobs.append(
                job
            )

    print()
    print(
        f"Already downloaded: "
        f"{existing}"
    )

    print(
        f"Missing: "
        f"{len(missing_jobs)}"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Before submitting anything,
    # clean up previously completed
    # GDEX requests.
    # --------------------------------------------------------

    reconcile_existing_requests()

    # Recalculate missing files
    missing_jobs = []

    for job in jobs:

        if not file_exists(
            job["day"],
            job["forecast_hour"]
        ):

            missing_jobs.append(
                job
            )

    print()
    print(
        f"Files still needed: "
        f"{len(missing_jobs)}"
    )

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------

    while missing_jobs:

        # ----------------------------------------------------
        # Always refresh completed requests first.
        # ----------------------------------------------------

        reconcile_existing_requests()

        # Recalculate
        missing_jobs = [
            job
            for job in jobs
            if not file_exists(
                job["day"],
                job["forecast_hour"]
            )
        ]

        if not missing_jobs:
            break

        # ----------------------------------------------------
        # Only submit up to 6 requests.
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Calculate available GDEX slots (max 10 allowed total on account)
        # ----------------------------------------------------

        total_on_server = count_open_requests()
        available_slots = max(0, 10 - total_on_server)

        if available_slots == 0:

            print()
            print(
                "GDEX server limit (10 requests) reached. "
                "Waiting 30 seconds for server to clear purged slots..."
            )

            time.sleep(CHECK_INTERVAL)
            continue

        # Submit at most available_slots (capped at BATCH_SIZE = 6)
        batch_size = min(BATCH_SIZE, available_slots)

        batch = missing_jobs[
            :batch_size
        ]

        # ----------------------------------------------------
        # Submit batch
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print(
            f"SUBMITTING "
            f"{len(batch)} REQUESTS "
            f"(available slots: {available_slots})"
        )
        print("=" * 70)

        submitted = []
        submission_failed = False

        for job in batch:

            req_info = submit_request(
                job["day"],
                job["forecast_hour"]
            )

            if req_info is None:

                print()
                print(
                    "Submission error encountered. "
                    "Will retry on next cycle."
                )

                submission_failed = True
                break

            submitted.append({
                "request_id":
                    req_info["request_id"],

                "request_index":
                    req_info["request_index"],

                "day":
                    job["day"],

                "forecast_hour":
                    job["forecast_hour"]
            })

        if submission_failed and not submitted:

            time.sleep(CHECK_INTERVAL)
            continue

        # ----------------------------------------------------
        # Wait for these requests
        # ----------------------------------------------------

        while True:

            status_data = get_status()

            finished = True

            for job in submitted:

                item = None

                for x in status_data:

                    if (
                        str(x.get("request_index")) == str(job["request_index"])
                        or str(x.get("request_id")) == str(job["request_id"])
                    ):

                        item = x
                        break

                if item is None:

                    if file_exists(job["day"], job["forecast_hour"]) or repair_malformed_file(job["day"], job["forecast_hour"]):
                        continue

                    finished = False
                    continue

                status = item.get(
                    "status",
                    ""
                )

                print(
                    f'{job["request_id"]} ({job["request_index"]}) | '
                    f'{job["day"]} | '
                    f'f{job["forecast_hour"]:03d} | '
                    f'{status}'
                )

                if status == "Completed":
                    continue

                if status in {
                    "Error",
                    "Failed",
                    "Cancelled"
                }:

                    print()
                    print(
                        f"GDEX request {job['request_id']} failed on server."
                    )

                    print(item)

                    purge_request(job["request_index"])

                    finished = True
                    break

                finished = False

            if finished:
                break

            print()
            print(
                f"Checking again in "
                f"{CHECK_INTERVAL} seconds..."
            )

            time.sleep(
                CHECK_INTERVAL
            )

        # ----------------------------------------------------
        # Download and purge
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print(
            "DOWNLOADING BATCH"
        )
        print("=" * 70)

        batch_failed = False
        for job in submitted:

            success = download_request(
                job["request_index"],
                job["day"],
                job["forecast_hour"]
            )

            if not success:

                print()
                print(
                    f"DOWNLOAD FAILED for {job['request_id']}. "
                    "Will retry on next main cycle."
                )

                batch_failed = True
                continue

            # Only purge after verified download
            purge_request(
                job["request_index"]
            )

        if batch_failed:
            print()
            print("Batch had download failures. Pausing 15s before next cycle...")
            time.sleep(15)
        else:
            print()
            print(
                "BATCH COMPLETED."
            )

        # ----------------------------------------------------
        # Small pause
        # ----------------------------------------------------

        time.sleep(3)

    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("=" * 70)
    print(
        "FINAL VERIFICATION"
    )
    print("=" * 70)

    remaining = []

    for job in jobs:

        if not file_exists(
            job["day"],
            job["forecast_hour"]
        ):

            remaining.append(
                job
            )

    if remaining:

        print()
        print(
            f"{len(remaining)} "
            f"files are still missing."
        )

        for job in remaining[:20]:

            print(
                job["day"],
                f'f{job["forecast_hour"]:03d}'
            )

    else:

        print()
        print(
            "SUCCESS!"
        )

        print(
            "All 244 August + September "
            "2024 GFS files are downloaded."
        )

    print()
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()