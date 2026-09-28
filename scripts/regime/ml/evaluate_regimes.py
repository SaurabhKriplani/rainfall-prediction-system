import pandas as pd
import numpy as np

from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error


# ============================================================
# FILES
# ============================================================

TRAIN = "data/processed/train_july_2024.csv"
VAL = "data/processed/val_july_2024.csv"
TEST = "data/processed/test_july_2024.csv"


# ============================================================
# LOAD DATA
# ============================================================

train_raw = pd.read_csv(TRAIN)
val_raw = pd.read_csv(VAL)
test_raw = pd.read_csv(TEST)

print("Train:", train_raw.shape)
print("Validation:", val_raw.shape)
print("Test:", test_raw.shape)


# ============================================================
# PRESERVE REGIME LABELS SEPARATELY
# ============================================================

train_regime = train_raw["synoptic_regime"].copy()
val_regime = val_raw["synoptic_regime"].copy()
test_regime = test_raw["synoptic_regime"].copy()


# ============================================================
# FEATURES
# ============================================================

numeric_features = [

    # GFS rainfall
    "gfs_rain_24h",

    # 850 hPa
    "z850",
    "r850",
    "t850",
    "u850",
    "v850",
    "w850",

    # 700 hPa
    "z700",
    "r700",
    "t700",
    "u700",
    "v700",
    "w700",

    # 500 hPa
    "z500",
    "r500",
    "t500",
    "u500",
    "v500",
    "w500",

    # Derived atmospheric features
    "wind850",
    "wind700",
    "wind500",
    "wind_dir850",

    "upward_motion850",
    "upward_motion700",
    "upward_motion500",

    "rh_lower_mid",
    "rh850_rh500_diff",

    "t850_t500_diff",
    "t850_t700_diff",

    "shear850_500",
    "shear850_700",

    "wind850_500_diff",
    "wind850_700_diff",

    # Geographic features
    "elevation_m",
    "coast_distance_km",
    "terrain_slope_deg"
]


# ============================================================
# ONE-HOT ENCODE REGIME
# ============================================================

combined = pd.concat(
    [train_raw, val_raw, test_raw],
    ignore_index=True
)

combined = pd.get_dummies(
    combined,
    columns=["synoptic_regime"],
    dtype=int
)


# ============================================================
# SPLIT BACK
# ============================================================

n_train = len(train_raw)
n_val = len(val_raw)

train = combined.iloc[
    :n_train
].copy()

val = combined.iloc[
    n_train:n_train + n_val
].copy()

test = combined.iloc[
    n_train + n_val:
].copy()


# ============================================================
# FIND ONE-HOT REGIME FEATURES
# ============================================================

regime_columns = [
    column
    for column in train.columns
    if column.startswith("synoptic_regime_")
]


print("\nRegime columns:")
print(regime_columns)


# ============================================================
# FINAL FEATURES
# ============================================================

features = numeric_features + regime_columns

print("\nNumber of features:", len(features))


# ============================================================
# MODEL DATA
# ============================================================

X_train = train[features]
X_val = val[features]
X_test = test[features]

y_train = train["bias"]
y_val = val["bias"]


# ============================================================
# TRAIN XGBOOST
# ============================================================

model = XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.03,
    min_child_weight=10,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=5.0,
    objective="reg:squarederror",
    eval_metric="rmse",
    random_state=42,
    n_jobs=-1
)


print("\nTraining XGBoost...")

model.fit(
    X_train,
    y_train,
    eval_set=[
        (X_val, y_val)
    ],
    verbose=False
)

print("Training complete.")


# ============================================================
# TEST PREDICTION
# ============================================================

test_bias_pred = model.predict(
    X_test
)


# ============================================================
# CREATE TEST RESULT DATAFRAME
# ============================================================

# Start from the ORIGINAL test dataframe.
# This guarantees synoptic_regime exists.

test_results = test_raw.copy()

test_results["predicted_bias"] = test_bias_pred

test_results["corrected_rainfall"] = np.maximum(
    test_results["gfs_rain_24h"]
    + test_results["predicted_bias"],
    0
)


# ============================================================
# METRIC FUNCTION
# ============================================================

def calculate_metrics(observed, predicted):

    rmse = np.sqrt(
        mean_squared_error(
            observed,
            predicted
        )
    )

    mae = mean_absolute_error(
        observed,
        predicted
    )

    return rmse, mae


# ============================================================
# OVERALL TEST PERFORMANCE
# ============================================================

gfs_rmse, gfs_mae = calculate_metrics(
    test_results["imd_rainfall"],
    test_results["gfs_rain_24h"]
)

corrected_rmse, corrected_mae = calculate_metrics(
    test_results["imd_rainfall"],
    test_results["corrected_rainfall"]
)


print("\n" + "=" * 70)
print("OVERALL TEST PERFORMANCE")
print("=" * 70)

print(
    f"Raw GFS RMSE:       {gfs_rmse:.4f}"
)

print(
    f"Corrected RMSE:     {corrected_rmse:.4f}"
)

print(
    f"Raw GFS MAE:        {gfs_mae:.4f}"
)

print(
    f"Corrected MAE:      {corrected_mae:.4f}"
)


# ============================================================
# REGIME-WISE EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("REGIME-WISE TEST PERFORMANCE")
print("=" * 70)


results = []


# IMPORTANT:
# Use the original test_results dataframe,
# NOT the one-hot encoded dataframe.

for regime in sorted(
    test_results["synoptic_regime"].unique()
):

    subset = test_results[
        test_results["synoptic_regime"] == regime
    ].copy()


    # --------------------------------------------------------
    # RAW GFS
    # --------------------------------------------------------

    raw_rmse, raw_mae = calculate_metrics(
        subset["imd_rainfall"],
        subset["gfs_rain_24h"]
    )


    # --------------------------------------------------------
    # CORRECTED
    # --------------------------------------------------------

    corrected_rmse, corrected_mae = calculate_metrics(
        subset["imd_rainfall"],
        subset["corrected_rainfall"]
    )


    # --------------------------------------------------------
    # IMPROVEMENT
    # --------------------------------------------------------

    rmse_improvement = (
        (raw_rmse - corrected_rmse)
        / raw_rmse
        * 100
    )

    mae_improvement = (
        (raw_mae - corrected_mae)
        / raw_mae
        * 100
    )


    # --------------------------------------------------------
    # STORE
    # --------------------------------------------------------

    results.append({

        "regime": regime,

        "samples": len(subset),

        "raw_rmse": raw_rmse,

        "corrected_rmse": corrected_rmse,

        "rmse_improvement_percent":
            rmse_improvement,

        "raw_mae": raw_mae,

        "corrected_mae": corrected_mae,

        "mae_improvement_percent":
            mae_improvement
    })


# ============================================================
# RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(results)


print(
    results_df.to_string(
        index=False,
        float_format=lambda x:
        f"{x:.4f}"
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    "data/processed/regime_wise_test_results.csv",
    index=False
)


test_results.to_csv(
    "data/processed/test_predictions_xgboost.csv",
    index=False
)


model.save_model(
    "data/processed/final_xgboost_bias_correction.json"
)


# ============================================================
# FINISHED
# ============================================================

print("\nSaved:")

print(
    "data/processed/regime_wise_test_results.csv"
)

print(
    "data/processed/test_predictions_xgboost.csv"
)

print(
    "data/processed/final_xgboost_bias_correction.json"
)