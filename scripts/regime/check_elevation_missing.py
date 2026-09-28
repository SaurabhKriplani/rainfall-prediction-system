import pandas as pd

file = "data/geography/dem/gfs_elevation_features.csv"

df = pd.read_csv(file)

missing = df[df["elevation_m"].isna()]

print("Total missing:", len(missing))

print("\nMissing latitude values:")
print(
    missing["latitude"]
    .value_counts()
    .sort_index()
)

print("\nMissing longitude values:")
print(
    missing["longitude"]
    .value_counts()
    .sort_index()
)

print("\nMissing coordinate ranges:")
print(
    "Latitude:",
    missing["latitude"].min(),
    "to",
    missing["latitude"].max()
)

print(
    "Longitude:",
    missing["longitude"].min(),
    "to",
    missing["longitude"].max()
)

print("\nFirst 30 missing cells:")
print(
    missing.head(30).to_string(index=False)
)