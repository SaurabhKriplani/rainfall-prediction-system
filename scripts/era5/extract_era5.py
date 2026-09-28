import xarray as xr
import pandas as pd

# Load ERA5 data
ds = xr.open_dataset("era5_test.nc")

# Convert ERA5 to a table
df = ds.to_dataframe().reset_index()

print("\n========== ORIGINAL DATA ==========")
print(df.head())
print("\nShape:", df.shape)

# Rename variables according to pressure level
feature_dfs = []

for level in [850, 700, 500]:
    level_df = df[df["pressure_level"] == level].copy()

    # Rename atmospheric variables
    rename_dict = {
        "z": f"z{level}",
        "r": f"r{level}",
        "t": f"t{level}",
        "u": f"u{level}",
        "v": f"v{level}",
        "w": f"w{level}",
    }

    level_df = level_df.rename(columns=rename_dict)

    # Keep only required columns
    columns = [
        "valid_time",
        "latitude",
        "longitude",
        f"z{level}",
        f"r{level}",
        f"t{level}",
        f"u{level}",
        f"v{level}",
        f"w{level}",
    ]

    level_df = level_df[columns]

    feature_dfs.append(level_df)

# Merge the three pressure levels
features = feature_dfs[0]

for level_df in feature_dfs[1:]:
    features = features.merge(
        level_df,
        on=["valid_time", "latitude", "longitude"],
        how="inner"
    )

# Rename time column
features = features.rename(columns={
    "valid_time": "date"
})

# Save
features.to_csv("era5_features_test.csv", index=False)

print("\n========== FINAL FEATURES ==========")
print(features.head())

print("\nShape:", features.shape)

print("\nColumns:")
print(features.columns.tolist())

print("\nSaved as:")
print("era5_features_test.csv")