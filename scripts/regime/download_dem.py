import os
import time
import requests
from dotenv import load_dotenv


# ============================================================
# LOAD CREDENTIALS
# ============================================================

load_dotenv()

CLIENT_ID = os.getenv("CDSE_CLIENT_ID")
CLIENT_SECRET = os.getenv("CDSE_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError(
        "CDSE_CLIENT_ID or CDSE_CLIENT_SECRET not found in .env"
    )


# ============================================================
# CDSE ENDPOINTS
# ============================================================

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

PROCESS_URL = "https://sh.dataspace.copernicus.eu/process/v1"


# ============================================================
# PROJECT AREA
# ============================================================

MIN_LON = 68.0
MIN_LAT = 6.0
MAX_LON = 98.0
MAX_LAT = 38.0


# ============================================================
# DOWNLOAD SETTINGS
# ============================================================

# 5° × 5° tiles
TILE_SIZE = 5.0

# 250 × 250 pixels per tile
#
# This gives roughly 0.02° (~2 km) resolution.
# We will later aggregate this to the 0.25° GFS grid.
OUTPUT_SIZE = 512

OUTPUT_DIR = "data/geography/dem"
TILE_DIR = os.path.join(OUTPUT_DIR, "tiles")

os.makedirs(TILE_DIR, exist_ok=True)


# ============================================================
# EVALSCRIPT
# ============================================================

EVALSCRIPT = """
//VERSION=3

function setup() {
    return {
        input: ["DEM"],
        output: {
            id: "default",
            bands: 1,
            sampleType: SampleType.FLOAT32
        }
    };
}

function evaluatePixel(sample) {
    return [sample.DEM];
}
"""


# ============================================================
# GET ACCESS TOKEN
# ============================================================

def get_access_token():

    print("Requesting CDSE access token...")

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=60,
    )

    response.raise_for_status()

    token = response.json()["access_token"]

    print("Access token obtained.")

    return token


# ============================================================
# DOWNLOAD ONE DEM TILE
# ============================================================

def download_tile(
    token,
    min_lon,
    min_lat,
    max_lon,
    max_lat,
    filename
):

    print(
        f"Downloading tile: "
        f"{min_lon},{min_lat} -> {max_lon},{max_lat}"
    )

    request_body = {

        "input": {

            "bounds": {

                "properties": {
                    "crs": (
                        "http://www.opengis.net/def/crs/"
                        "OGC/1.3/CRS84"
                    )
                },

                "bbox": [
                    min_lon,
                    min_lat,
                    max_lon,
                    max_lat
                ]
            },

            "data": [

                {
                    "type": "dem",

                    "dataFilter": {
                        "demInstance": "COPERNICUS_90"
                    },

                    "processing": {
                        "upsampling": "BILINEAR",
                        "downsampling": "BILINEAR"
                    }
                }

            ]
        },

        "output": {

            "width": OUTPUT_SIZE,
            "height": OUTPUT_SIZE,

            "responses": [

                {
                    "identifier": "default",

                    "format": {
                        "type": "image/tiff"
                    }
                }

            ]
        },

        "evalscript": EVALSCRIPT
    }


    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "image/tiff"
    }


    for attempt in range(3):

        try:

            response = requests.post(
                PROCESS_URL,
                headers=headers,
                json=request_body,
                timeout=180
            )


            # ------------------------------------------------
            # Print useful error from CDSE
            # ------------------------------------------------

            if response.status_code != 200:

                print(
                    f"CDSE response: "
                    f"{response.status_code}"
                )

                print(
                    "Response body:"
                )

                print(response.text[:3000])


            # ------------------------------------------------
            # Token expired
            # ------------------------------------------------

            if response.status_code == 401:

                print(
                    "Token expired. "
                    "Getting a new token..."
                )

                token = get_access_token()

                headers["Authorization"] = (
                    f"Bearer {token}"
                )

                continue


            response.raise_for_status()


            # ------------------------------------------------
            # Save TIFF
            # ------------------------------------------------

            with open(filename, "wb") as f:
                f.write(response.content)


            print(
                f"Saved: {filename}"
            )

            return token


        except Exception as e:

            print(
                f"Attempt {attempt + 1}/3 failed: {e}"
            )

            if attempt < 2:
                time.sleep(5)

            else:
                raise


# ============================================================
# MAIN
# ============================================================

def main():

    token = get_access_token()

    tile_number = 0

    lat = MIN_LAT

    while lat < MAX_LAT:

        next_lat = min(
            lat + TILE_SIZE,
            MAX_LAT
        )

        lon = MIN_LON

        while lon < MAX_LON:

            next_lon = min(
                lon + TILE_SIZE,
                MAX_LON
            )

            tile_number += 1

            filename = os.path.join(
                TILE_DIR,
                f"dem_{tile_number:02d}.tif"
            )


            # ----------------------------------------------
            # Skip existing tiles
            # ----------------------------------------------

            if os.path.exists(filename):

                print(
                    f"Already exists: {filename}"
                )

            else:

                token = download_tile(
                    token,
                    lon,
                    lat,
                    next_lon,
                    next_lat,
                    filename
                )


            lon = next_lon

        lat = next_lat


    print()
    print("=" * 60)
    print("ALL DEM TILES DOWNLOADED")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()