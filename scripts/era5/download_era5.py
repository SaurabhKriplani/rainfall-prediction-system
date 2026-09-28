import cdsapi

client = cdsapi.Client()

dataset = "reanalysis-era5-pressure-levels"

request = {
    "product_type": ["reanalysis"],

    "variable": [
        "geopotential",
        "relative_humidity",
        "temperature",
        "u_component_of_wind",
        "v_component_of_wind",
        "vertical_velocity"
    ],

    "year": ["2024"],
    "month": ["07"],

    # TEST ONLY: July 1 and July 31
    "day": [
    "01", "02", "03", "04", "05",
    "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15",
    "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25",
    "26", "27", "28", "29", "30", "31"
    ],

    "time": [
        "00:00",
        "06:00",
        "12:00",
        "18:00"
    ],

    "pressure_level": [
        "500",
        "700",
        "850"
    ],

    "data_format": "netcdf",
    "download_format": "unarchived",

    "area": [39, 66, 6, 101]
}

print("Requesting ERA5 data...")

client.retrieve(
    dataset,
    request,
    "era5_test.nc"
)

print("Download complete!")