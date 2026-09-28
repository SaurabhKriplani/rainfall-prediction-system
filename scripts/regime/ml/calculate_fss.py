import pandas as pd
import numpy as np

INPUT = "data/final/bias_corrected_sep_2024.csv"
OUTPUT = "data/final/fss_results.csv"

df = pd.read_csv(INPUT)
df["date"] = pd.to_datetime(df["date"])

# ------------------------------------------------------------
# FSS
# ------------------------------------------------------------

def calculate_fss(forecast, observed, threshold, window=3):

    forecast_event = (forecast >= threshold).astype(float)
    observed_event = (observed >= threshold).astype(float)

    # Fraction of event cells in neighborhood
    f_fraction = (
        forecast_event
        .rolling(window=window, center=True, min_periods=1)
        .mean()
    )

    o_fraction = (
        observed_event
        .rolling(window=window, center=True, min_periods=1)
        .mean()
    )

    mse = np.mean((f_fraction - o_fraction) ** 2)

    reference = (
        np.mean(f_fraction ** 2) +
        np.mean(o_fraction ** 2)
    )

    if reference == 0:
        return np.nan

    return 1 - mse / reference


# ------------------------------------------------------------
# IMPORTANT:
# FSS needs spatial neighborhoods.
# Calculate separately for every date.
# ------------------------------------------------------------

thresholds = [
    (64.5, "Heavy"),
    (115.6, "Very Heavy"),
    (204.5, "Extremely Heavy")
]

results = []

for threshold, name in thresholds:

    raw_scores = []
    corrected_scores = []

    for date, day in df.groupby("date"):

        # Create grid
        raw_grid = day.pivot_table(
            index="latitude",
            columns="longitude",
            values="gfs_rain_24h"
        ).sort_index()

        corrected_grid = day.pivot_table(
            index="latitude",
            columns="longitude",
            values="corrected_rainfall"
        ).sort_index()

        obs_grid = day.pivot_table(
            index="latitude",
            columns="longitude",
            values="imd_rainfall"
        ).sort_index()

        # Ensure same grid
        common_lat = raw_grid.index.intersection(
            obs_grid.index
        )

        common_lon = raw_grid.columns.intersection(
            obs_grid.columns
        )

        raw_grid = raw_grid.loc[
            common_lat, common_lon
        ]

        corrected_grid = corrected_grid.loc[
            common_lat, common_lon
        ]

        obs_grid = obs_grid.loc[
            common_lat, common_lon
        ]

        # Convert to arrays
        raw = raw_grid.values
        corrected = corrected_grid.values
        obs = obs_grid.values

        # Event fields
        raw_event = (raw >= threshold).astype(float)
        corrected_event = (corrected >= threshold).astype(float)
        obs_event = (obs >= threshold).astype(float)

        # 3x3 neighborhood
        def fractions(field):

            padded = np.pad(
                field,
                1,
                mode="constant",
                constant_values=0
            )

            result = np.zeros_like(field, dtype=float)

            for i in range(field.shape[0]):
                for j in range(field.shape[1]):

                    neighborhood = padded[
                        i:i+3,
                        j:j+3
                    ]

                    result[i, j] = neighborhood.mean()

            return result

        raw_fraction = fractions(raw_event)
        corrected_fraction = fractions(corrected_event)
        obs_fraction = fractions(obs_event)

        # Raw GFS FSS
        raw_mse = np.mean(
            (raw_fraction - obs_fraction) ** 2
        )

        raw_ref = (
            np.mean(raw_fraction ** 2) +
            np.mean(obs_fraction ** 2)
        )

        raw_fss = (
            1 - raw_mse / raw_ref
            if raw_ref > 0 else np.nan
        )

        # Corrected FSS
        corrected_mse = np.mean(
            (corrected_fraction - obs_fraction) ** 2
        )

        corrected_ref = (
            np.mean(corrected_fraction ** 2) +
            np.mean(obs_fraction ** 2)
        )

        corrected_fss = (
            1 - corrected_mse / corrected_ref
            if corrected_ref > 0 else np.nan
        )

        if not np.isnan(raw_fss):
            raw_scores.append(raw_fss)

        if not np.isnan(corrected_fss):
            corrected_scores.append(corrected_fss)

    results.append({
        "threshold_mm": threshold,
        "category": name,
        "raw_FSS": np.mean(raw_scores),
        "corrected_FSS": np.mean(corrected_scores)
    })


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

results_df = pd.DataFrame(results)

results_df.to_csv(
    OUTPUT,
    index=False
)

print("\n======================================")
print("FSS RESULTS")
print("======================================")

print(results_df.to_string(index=False))

print("\nSaved:")
print(OUTPUT)