import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

INPUT = "data/final/bias_corrected_sep_2024.csv"
OUTPUT = "data/final/verification_results.csv"

df = pd.read_csv(INPUT)

obs = df["imd_rainfall"].values
raw = df["gfs_rain_24h"].values
corrected = df["corrected_rainfall"].values


def scores(forecast, observation, threshold):

    f = forecast >= threshold
    o = observation >= threshold

    hits = np.sum(f & o)
    false_alarm = np.sum(f & ~o)
    miss = np.sum(~f & o)
    correct_negative = np.sum(~f & ~o)

    # CSI
    csi = hits / (hits + false_alarm + miss) if (hits + false_alarm + miss) else 0

    # POD
    pod = hits / (hits + miss) if (hits + miss) else 0

    # FAR
    far = false_alarm / (hits + false_alarm) if (hits + false_alarm) else 0

    # ETS
    total = hits + false_alarm + miss + correct_negative

    hits_random = (
        (hits + false_alarm) *
        (hits + miss) /
        total
    ) if total else 0

    ets = (
        (hits - hits_random) /
        (hits + false_alarm + miss - hits_random)
        if (hits + false_alarm + miss - hits_random) else 0
    )

    return csi, pod, far, ets


print("======================================")
print("FORECAST VERIFICATION")
print("======================================")


# ============================================================
# OVERALL RMSE / MAE
# ============================================================

raw_rmse = np.sqrt(mean_squared_error(obs, raw))
corrected_rmse = np.sqrt(mean_squared_error(obs, corrected))

raw_mae = mean_absolute_error(obs, raw)
corrected_mae = mean_absolute_error(obs, corrected)

print("\nOVERALL")
print("--------------------------------------")

print(f"Raw GFS RMSE       : {raw_rmse:.4f}")
print(f"Corrected RMSE     : {corrected_rmse:.4f}")

print(f"Raw GFS MAE        : {raw_mae:.4f}")
print(f"Corrected MAE      : {corrected_mae:.4f}")


# ============================================================
# HEAVY RAINFALL
# ============================================================

thresholds = [
    (64.5, "Heavy"),
    (115.6, "Very Heavy"),
    (204.5, "Extremely Heavy")
]

results = []

for threshold, name in thresholds:

    raw_scores = scores(raw, obs, threshold)
    corrected_scores = scores(corrected, obs, threshold)

    print(f"\n{name} Rainfall (>= {threshold} mm)")
    print("--------------------------------------")

    print("                 Raw GFS    Corrected")

    print(
        f"CSI              {raw_scores[0]:.4f}       "
        f"{corrected_scores[0]:.4f}"
    )

    print(
        f"POD              {raw_scores[1]:.4f}       "
        f"{corrected_scores[1]:.4f}"
    )

    print(
        f"FAR              {raw_scores[2]:.4f}       "
        f"{corrected_scores[2]:.4f}"
    )

    print(
        f"ETS              {raw_scores[3]:.4f}       "
        f"{corrected_scores[3]:.4f}"
    )

    results.append({
        "threshold_mm": threshold,
        "category": name,

        "raw_CSI": raw_scores[0],
        "corrected_CSI": corrected_scores[0],

        "raw_POD": raw_scores[1],
        "corrected_POD": corrected_scores[1],

        "raw_FAR": raw_scores[2],
        "corrected_FAR": corrected_scores[2],

        "raw_ETS": raw_scores[3],
        "corrected_ETS": corrected_scores[3]
    })


# ============================================================
# SAVE
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(OUTPUT, index=False)

print("\n======================================")
print("Saved:")
print(OUTPUT)

print("\nVerification table:")
print(results_df.to_string(index=False))