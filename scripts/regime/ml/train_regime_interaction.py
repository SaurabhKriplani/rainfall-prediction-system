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

OUTPUT_RESULTS = (
    "data/processed/regime_interaction_results.csv"
)

OUTPUT_PREDICTIONS = (
    "data/processed/test_predictions_regime_interaction.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

train = pd.read_csv(TRAIN)
val = pd.read_csv(VAL)
test = pd.read_csv(TEST)

print("Train:", train.shape)
print("Validation:", val.shape)
print("Test:", test.shape)


# ============================================================
# BASE NUMERIC FEATURES
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

    # Geography
    "elevation_m",
    "coast_distance_km",
    "terrain_slope_deg"
]


# ============================================================
# CHECK COLUMNS
# ============================================================

required_columns = numeric_features + [
    "bias",
    "imd_rainfall",
    "gfs_rain_24h",
    "synoptic_regime"
]

for column in required_columns:

    if column not in train.columns:
        raise ValueError(
            f"Missing column in train: {column}"
        )

    if column not in val.columns:
        raise ValueError(
            f"Missing column in validation: {column}"
        )

    if column not in test.columns:
        raise ValueError(
            f"Missing column in test: {column}"
        )

print("\nAll required columns found.")


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
# CREATE REGIME INTERACTION FEATURES
# ============================================================

def create_regime_interactions(df):

    df = df.copy()

    regimes = sorted(
        df["synoptic_regime"].unique()
    )

    # --------------------------------------------------------
    # One-hot regime columns
    # --------------------------------------------------------

    regime_dummies = pd.get_dummies(
        df["synoptic_regime"],
        prefix="regime",
        dtype=int
    )

    # --------------------------------------------------------
    # Add one-hot columns
    # --------------------------------------------------------

    for column in regime_dummies.columns:

        df[column] = regime_dummies[
            column
        ].values

    # --------------------------------------------------------
    # Features for interactions
    #
    # We don't need to interact EVERY feature.
    # These are physically relevant for rainfall response.
    # --------------------------------------------------------

    interaction_features = [

        "gfs_rain_24h",

        "r850",
        "r700",
        "r500",

        "w850",
        "w700",
        "w500",

        "upward_motion850",
        "upward_motion700",
        "upward_motion500",

        "wind850",
        "wind700",
        "wind500",

        "shear850_500",

        "elevation_m",
        "coast_distance_km",
        "terrain_slope_deg"
    ]

    # --------------------------------------------------------
    # Create interactions
    #
    # Example:
    #
    # gfs_rain_24h × regime_low_pressure
    #
    # --------------------------------------------------------

    for regime_column in regime_dummies.columns:

        for feature in interaction_features:

            interaction_name = (
                f"{feature}__x__{regime_column}"
            )

            df[interaction_name] = (
                df[feature]
                * df[regime_column]
            )

    return df


# ============================================================
# CREATE FEATURES
# ============================================================

print("\n")
print("=" * 70)
print("CREATING REGIME INTERACTION FEATURES")
print("=" * 70)

train_features = create_regime_interactions(
    train
)

val_features = create_regime_interactions(
    val
)

test_features = create_regime_interactions(
    test
)


# ============================================================
# MAKE SURE ALL DATASETS HAVE SAME COLUMNS
# ============================================================

# Sometimes a regime can be absent from one split.
# Therefore align columns explicitly.

train_features, val_features = (
    train_features.align(
        val_features,
        join="outer",
        axis=1,
        fill_value=0
    )
)

train_features, test_features = (
    train_features.align(
        test_features,
        join="outer",
        axis=1,
        fill_value=0
    )
)

val_features, test_features = (
    val_features.align(
        test_features,
        join="outer",
        axis=1,
        fill_value=0
    )
)


# ============================================================
# FIND REGIME COLUMNS
# ============================================================

regime_columns = [

    column

    for column in train_features.columns

    if column.startswith("regime_")
]


# ============================================================
# FIND INTERACTION COLUMNS
# ============================================================

interaction_columns = [

    column

    for column in train_features.columns

    if "__x__" in column
]


print(
    "\nNumber of regime columns:",
    len(regime_columns)
)

print(
    "Number of interaction columns:",
    len(interaction_columns)
)

print(
    "Total features:",
    len(
        numeric_features
        + regime_columns
        + interaction_columns
    )
)


# ============================================================
# FINAL FEATURE LIST
# ============================================================

features = (
    numeric_features
    + regime_columns
    + interaction_columns
)


# Remove duplicates while preserving order

features = list(
    dict.fromkeys(features)
)


# ============================================================
# PREPARE MODEL DATA
# ============================================================

X_train = train_features[
    features
]

X_val = val_features[
    features
]

X_test = test_features[
    features
]

y_train = train_features[
    "bias"
]

y_val = val_features[
    "bias"
]


print("\nFinal feature matrix:")

print(
    "X_train:",
    X_train.shape
)

print(
    "X_val:",
    X_val.shape
)

print(
    "X_test:",
    X_test.shape
)


# ============================================================
# CREATE XGBOOST MODEL
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


# ============================================================
# TRAIN
# ============================================================

print("\n")
print("=" * 70)
print("TRAINING REGIME-INTERACTION XGBOOST")
print("=" * 70)

model.fit(

    X_train,

    y_train,

    eval_set=[
        (
            X_val,
            y_val
        )
    ],

    verbose=False
)

print(
    "Training complete."
)


# ============================================================
# PREDICT BIAS
# ============================================================

predicted_bias = model.predict(
    X_test
)


# ============================================================
# CORRECTED RAINFALL
# ============================================================

corrected_rainfall = np.maximum(

    test[
        "gfs_rain_24h"
    ].values

    + predicted_bias,

    0
)


# ============================================================
# TEST RESULTS
# ============================================================

test_results = test.copy()

test_results[
    "predicted_bias"
] = predicted_bias

test_results[
    "corrected_rainfall"
] = corrected_rainfall


# ============================================================
# RAW GFS METRICS
# ============================================================

raw_rmse, raw_mae = calculate_metrics(

    test_results[
        "imd_rainfall"
    ],

    test_results[
        "gfs_rain_24h"
    ]
)


# ============================================================
# INTERACTION MODEL METRICS
# ============================================================

corrected_rmse, corrected_mae = calculate_metrics(

    test_results[
        "imd_rainfall"
    ],

    test_results[
        "corrected_rainfall"
    ]
)


# ============================================================
# IMPROVEMENT
# ============================================================

rmse_improvement = (

    (
        raw_rmse
        - corrected_rmse
    )

    / raw_rmse

    * 100
)


mae_improvement = (

    (
        raw_mae
        - corrected_mae
    )

    / raw_mae

    * 100
)


# ============================================================
# OVERALL RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("OVERALL TEST PERFORMANCE")
print("=" * 70)

print(
    f"Raw GFS RMSE:              "
    f"{raw_rmse:.4f}"
)

print(
    f"Interaction XGBoost RMSE:  "
    f"{corrected_rmse:.4f}"
)

print(
    f"RMSE improvement:           "
    f"{rmse_improvement:.2f}%"
)

print()

print(
    f"Raw GFS MAE:               "
    f"{raw_mae:.4f}"
)

print(
    f"Interaction XGBoost MAE:   "
    f"{corrected_mae:.4f}"
)

print(
    f"MAE improvement:            "
    f"{mae_improvement:.2f}%"
)


# ============================================================
# REGIME-WISE RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("REGIME-WISE TEST PERFORMANCE")
print("=" * 70)


regime_results = []


for regime in sorted(

    test_results[
        "synoptic_regime"
    ].unique()

):

    subset = test_results[
        test_results[
            "synoptic_regime"
        ] == regime
    ].copy()


    raw_r, raw_m = calculate_metrics(

        subset[
            "imd_rainfall"
        ],

        subset[
            "gfs_rain_24h"
        ]
    )


    corrected_r, corrected_m = calculate_metrics(

        subset[
            "imd_rainfall"
        ],

        subset[
            "corrected_rainfall"
        ]
    )


    rmse_imp = (

        (
            raw_r
            - corrected_r
        )

        / raw_r

        * 100
    )


    mae_imp = (

        (
            raw_m
            - corrected_m
        )

        / raw_m

        * 100
    )


    regime_results.append({

        "regime": regime,

        "samples": len(subset),

        "raw_rmse": raw_r,

        "corrected_rmse": corrected_r,

        "rmse_improvement_percent": rmse_imp,

        "raw_mae": raw_m,

        "corrected_mae": corrected_m,

        "mae_improvement_percent": mae_imp
    })


regime_results_df = pd.DataFrame(
    regime_results
)


print(

    regime_results_df.to_string(

        index=False,

        float_format=lambda x:
        f"{x:.4f}"
    )
)


# ============================================================
# COMPARE AGAINST EXISTING GENERIC MODEL
# ============================================================

print("\n")
print("=" * 70)
print("COMPARISON WITH EXISTING BASELINE")
print("=" * 70)

print(
    f"Raw GFS RMSE:              {raw_rmse:.4f}"
)

print(
    f"Generic XGBoost RMSE:      15.9785"
)

print(
    f"Interaction XGBoost RMSE:  {corrected_rmse:.4f}"
)

print()

print(
    f"Raw GFS MAE:               {raw_mae:.4f}"
)

print(
    f"Generic XGBoost MAE:       9.7180"
)

print(
    f"Interaction XGBoost MAE:   {corrected_mae:.4f}"
)


# ============================================================
# SAVE RESULTS
# ============================================================

regime_results_df.to_csv(

    OUTPUT_RESULTS,

    index=False
)


test_results.to_csv(

    OUTPUT_PREDICTIONS,

    index=False
)


model.save_model(

    "data/processed/"
    "regime_interaction_xgboost.json"
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importance_df = pd.DataFrame({

    "feature": features,

    "importance": model.feature_importances_
})


importance_df = importance_df.sort_values(

    "importance",

    ascending=False
)


importance_df.to_csv(

    "data/processed/"
    "regime_interaction_feature_importance.csv",

    index=False
)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 70)
print("SAVED")
print("=" * 70)

print(
    OUTPUT_RESULTS
)

print(
    OUTPUT_PREDICTIONS
)

print(
    "data/processed/"
    "regime_interaction_xgboost.json"
)

print(
    "data/processed/"
    "regime_interaction_feature_importance.csv"
)

print("\nDone.")