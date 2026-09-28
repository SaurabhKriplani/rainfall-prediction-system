import os
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

OUTPUT_COMPARISON = (
    "data/processed/regime_model_comparison.csv"
)

OUTPUT_REGIME_RESULTS = (
    "data/processed/regime_model_regime_wise_results.csv"
)

OUTPUT_PREDICTIONS = (
    "data/processed/test_predictions_regime_models.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

train_raw = pd.read_csv(TRAIN)
val_raw = pd.read_csv(VAL)
test_raw = pd.read_csv(TEST)

print("Train:", train_raw.shape)
print("Validation:", val_raw.shape)
print("Test:", test_raw.shape)


# ============================================================
# FEATURES
# ============================================================

numeric_features = [

    # --------------------------------------------------------
    # GFS rainfall
    # --------------------------------------------------------

    "gfs_rain_24h",

    # --------------------------------------------------------
    # 850 hPa
    # --------------------------------------------------------

    "z850",
    "r850",
    "t850",
    "u850",
    "v850",
    "w850",

    # --------------------------------------------------------
    # 700 hPa
    # --------------------------------------------------------

    "z700",
    "r700",
    "t700",
    "u700",
    "v700",
    "w700",

    # --------------------------------------------------------
    # 500 hPa
    # --------------------------------------------------------

    "z500",
    "r500",
    "t500",
    "u500",
    "v500",
    "w500",

    # --------------------------------------------------------
    # Derived atmospheric features
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Geographic features
    # --------------------------------------------------------

    "elevation_m",
    "coast_distance_km",
    "terrain_slope_deg"
]


# ============================================================
# CHECK FEATURES
# ============================================================

print("\nChecking required features...")

required_columns = (
    numeric_features
    + [
        "bias",
        "imd_rainfall",
        "synoptic_regime"
    ]
)

for column in required_columns:

    if column not in train_raw.columns:
        raise ValueError(
            f"Missing column in training data: {column}"
        )

    if column not in val_raw.columns:
        raise ValueError(
            f"Missing column in validation data: {column}"
        )

    if column not in test_raw.columns:
        raise ValueError(
            f"Missing column in test data: {column}"
        )

print("All required columns found.")


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
# XGBOOST MODEL FUNCTION
# ============================================================

def create_xgboost_model():

    return XGBRegressor(

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
# ============================================================
# MODEL 1
# GENERIC XGBOOST
# ============================================================
#
# One XGBoost model for ALL regimes.
#
# Regime is supplied as a one-hot encoded feature.
# ============================================================

print("\n")
print("=" * 70)
print("MODEL 1: GENERIC XGBOOST")
print("=" * 70)


# ------------------------------------------------------------
# Combine train / validation / test ONLY to make sure
# one-hot columns are identical.
# ------------------------------------------------------------

combined = pd.concat(
    [
        train_raw,
        val_raw,
        test_raw
    ],
    ignore_index=True
)


combined = pd.get_dummies(
    combined,
    columns=["synoptic_regime"],
    dtype=int
)


# ------------------------------------------------------------
# Split back
# ------------------------------------------------------------

n_train = len(train_raw)
n_val = len(val_raw)

train_generic = combined.iloc[
    :n_train
].copy()

val_generic = combined.iloc[
    n_train:n_train + n_val
].copy()

test_generic = combined.iloc[
    n_train + n_val:
].copy()


# ------------------------------------------------------------
# Find regime columns
# ------------------------------------------------------------

regime_columns = [

    column

    for column in train_generic.columns

    if column.startswith(
        "synoptic_regime_"
    )
]


print("\nRegime columns:")

for column in regime_columns:
    print(" ", column)


# ------------------------------------------------------------
# Generic model features
# ------------------------------------------------------------

generic_features = (
    numeric_features
    + regime_columns
)


print(
    "\nNumber of generic features:",
    len(generic_features)
)


# ------------------------------------------------------------
# Prepare data
# ------------------------------------------------------------

X_train_generic = train_generic[
    generic_features
]

X_val_generic = val_generic[
    generic_features
]

X_test_generic = test_generic[
    generic_features
]

y_train_generic = train_generic[
    "bias"
]

y_val_generic = val_generic[
    "bias"
]


# ------------------------------------------------------------
# Create model
# ------------------------------------------------------------

generic_model = create_xgboost_model()


print("\nTraining generic XGBoost...")


generic_model.fit(

    X_train_generic,

    y_train_generic,

    eval_set=[
        (
            X_val_generic,
            y_val_generic
        )
    ],

    verbose=False
)


print("Generic XGBoost training complete.")


# ------------------------------------------------------------
# Predict bias
# ------------------------------------------------------------

generic_predicted_bias = generic_model.predict(
    X_test_generic
)


# ------------------------------------------------------------
# Convert predicted bias to rainfall
# ------------------------------------------------------------

generic_corrected_rainfall = np.maximum(

    test_raw[
        "gfs_rain_24h"
    ].values

    + generic_predicted_bias,

    0
)


# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------

generic_rmse, generic_mae = calculate_metrics(

    test_raw[
        "imd_rainfall"
    ],

    generic_corrected_rainfall
)


print(
    f"\nGeneric XGBoost RMSE: "
    f"{generic_rmse:.4f}"
)

print(
    f"Generic XGBoost MAE:  "
    f"{generic_mae:.4f}"
)


# ============================================================
# ============================================================
# MODEL 2
# REGIME-SPECIFIC XGBOOST
# ============================================================
#
# A separate XGBoost model is trained for each regime.
#
# Example:
#
# background_monsoon -> Model 1
# low_pressure       -> Model 2
# depression         -> Model 3
#
# ============================================================

print("\n")
print("=" * 70)
print("MODEL 2: REGIME-SPECIFIC XGBOOST")
print("=" * 70)


# ------------------------------------------------------------
# Find all regimes
# ------------------------------------------------------------

regimes = sorted(
    train_raw[
        "synoptic_regime"
    ].unique()
)


print("\nRegimes found in training data:")

for regime in regimes:

    count = (
        train_raw[
            "synoptic_regime"
        ] == regime
    ).sum()

    print(
        f"  {regime}: {count} samples"
    )


# ------------------------------------------------------------
# Create empty prediction array
#
# One position for every test row.
# ------------------------------------------------------------

regime_specific_predictions = np.full(

    len(test_raw),

    np.nan
)


# ------------------------------------------------------------
# Store models
# ------------------------------------------------------------

regime_models = {}


# ============================================================
# TRAIN ONE MODEL PER REGIME
# ============================================================

for regime in regimes:

    print("\n")
    print("-" * 70)

    print(
        f"REGIME: {regime}"
    )

    print("-" * 70)


    # --------------------------------------------------------
    # Select regime data
    # --------------------------------------------------------

    train_mask = (
        train_raw[
            "synoptic_regime"
        ] == regime
    )

    val_mask = (
        val_raw[
            "synoptic_regime"
        ] == regime
    )

    test_mask = (
        test_raw[
            "synoptic_regime"
        ] == regime
    )


    train_subset = train_raw[
        train_mask
    ].copy()

    val_subset = val_raw[
        val_mask
    ].copy()

    test_subset = test_raw[
        test_mask
    ].copy()


    print(
        "Train samples:",
        len(train_subset)
    )

    print(
        "Validation samples:",
        len(val_subset)
    )

    print(
        "Test samples:",
        len(test_subset)
    )


    # --------------------------------------------------------
    # If no test samples, there is nothing to evaluate.
    # --------------------------------------------------------

    if len(test_subset) == 0:

        print(
            "No test samples for this regime."
        )

        print(
            "Skipping prediction."
        )

        continue


    # --------------------------------------------------------
    # Create regime model
    # --------------------------------------------------------

    regime_model = create_xgboost_model()


    # --------------------------------------------------------
    # Training data
    # --------------------------------------------------------

    X_train_regime = train_subset[
        numeric_features
    ]

    y_train_regime = train_subset[
        "bias"
    ]


    # --------------------------------------------------------
    # Validation available
    # --------------------------------------------------------

    if len(val_subset) > 0:

        print(
            "Validation data available."
        )

        X_val_regime = val_subset[
            numeric_features
        ]

        y_val_regime = val_subset[
            "bias"
        ]


        regime_model.fit(

            X_train_regime,

            y_train_regime,

            eval_set=[
                (
                    X_val_regime,
                    y_val_regime
                )
            ],

            verbose=False
        )


    # --------------------------------------------------------
    # Validation NOT available
    # --------------------------------------------------------

    else:

        print(
            "No validation data for this regime."
        )

        print(
            "Training without validation set."
        )


        regime_model.fit(

            X_train_regime,

            y_train_regime,

            verbose=False
        )


    print(
        f"{regime} model training complete."
    )


    # --------------------------------------------------------
    # Save model in dictionary
    # --------------------------------------------------------

    regime_models[
        regime
    ] = regime_model


    # --------------------------------------------------------
    # Test prediction
    # --------------------------------------------------------

    X_test_regime = test_subset[
        numeric_features
    ]


    predicted_bias = regime_model.predict(
        X_test_regime
    )


    # --------------------------------------------------------
    # Convert bias to rainfall
    # --------------------------------------------------------

    predicted_rainfall = np.maximum(

        test_subset[
            "gfs_rain_24h"
        ].values

        + predicted_bias,

        0
    )


    # --------------------------------------------------------
    # Find original test row indices
    # --------------------------------------------------------

    test_indices = np.where(
        test_mask.values
    )[0]


    # --------------------------------------------------------
    # Store predictions
    # --------------------------------------------------------

    regime_specific_predictions[
        test_indices
    ] = predicted_rainfall


    # --------------------------------------------------------
    # Regime-specific immediate metrics
    # --------------------------------------------------------

    regime_rmse, regime_mae = calculate_metrics(

        test_subset[
            "imd_rainfall"
        ],

        predicted_rainfall
    )


    print(
        f"{regime} test RMSE: "
        f"{regime_rmse:.4f}"
    )

    print(
        f"{regime} test MAE: "
        f"{regime_mae:.4f}"
    )


# ============================================================
# CREATE TEST RESULTS
# ============================================================

test_results = test_raw.copy()


# Generic XGBoost prediction

test_results[
    "generic_xgb_rainfall"
] = generic_corrected_rainfall


# Regime-specific prediction

test_results[
    "regime_specific_xgb_rainfall"
] = regime_specific_predictions


# ============================================================
# CHECK MISSING PREDICTIONS
# ============================================================

missing_predictions = (

    test_results[
        "regime_specific_xgb_rainfall"
    ].isna().sum()

)


print("\n")
print("=" * 70)

print(
    "REGIME-SPECIFIC PREDICTION CHECK"
)

print("=" * 70)

print(
    "Missing predictions:",
    missing_predictions
)


if missing_predictions > 0:

    print(
        "\nWARNING:"
    )

    print(
        "Some test rows do not have a regime-specific "
        "prediction."
    )


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
# GENERIC XGBOOST METRICS
# ============================================================

generic_rmse, generic_mae = calculate_metrics(

    test_results[
        "imd_rainfall"
    ],

    test_results[
        "generic_xgb_rainfall"
    ]
)


# ============================================================
# REGIME-SPECIFIC XGBOOST METRICS
# ============================================================

valid_regime_predictions = (

    test_results[
        "regime_specific_xgb_rainfall"
    ].notna()

)


regime_specific_rmse, regime_specific_mae = (
    calculate_metrics(

        test_results.loc[
            valid_regime_predictions,
            "imd_rainfall"
        ],

        test_results.loc[
            valid_regime_predictions,
            "regime_specific_xgb_rainfall"
        ]
    )
)


# ============================================================
# MODEL COMPARISON TABLE
# ============================================================

comparison_df = pd.DataFrame({

    "model": [

        "Raw GFS",

        "Generic XGBoost",

        "Regime-Specific XGBoost"
    ],

    "test_rmse": [

        raw_rmse,

        generic_rmse,

        regime_specific_rmse
    ],

    "test_mae": [

        raw_mae,

        generic_mae,

        regime_specific_mae
    ]
})


# ============================================================
# IMPROVEMENT RELATIVE TO RAW GFS
# ============================================================

comparison_df[
    "rmse_improvement_percent"
] = (

    (
        raw_rmse
        - comparison_df[
            "test_rmse"
        ]
    )

    / raw_rmse

    * 100
)


comparison_df[
    "mae_improvement_percent"
] = (

    (
        raw_mae
        - comparison_df[
            "test_mae"
        ]
    )

    / raw_mae

    * 100
)


# ============================================================
# PRINT OVERALL RESULTS
# ============================================================

print("\n")
print("=" * 70)

print(
    "MODEL COMPARISON"
)

print("=" * 70)


print(

    comparison_df.to_string(

        index=False,

        float_format=lambda x:
        f"{x:.4f}"
    )
)


# ============================================================
# REGIME-WISE COMPARISON
# ============================================================

print("\n")
print("=" * 70)

print(
    "REGIME-WISE COMPARISON"
)

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


    # --------------------------------------------------------
    # Raw GFS
    # --------------------------------------------------------

    raw_r, raw_m = calculate_metrics(

        subset[
            "imd_rainfall"
        ],

        subset[
            "gfs_rain_24h"
        ]
    )


    # --------------------------------------------------------
    # Generic XGBoost
    # --------------------------------------------------------

    generic_r, generic_m = calculate_metrics(

        subset[
            "imd_rainfall"
        ],

        subset[
            "generic_xgb_rainfall"
        ]
    )


    # --------------------------------------------------------
    # Regime-specific XGBoost
    # --------------------------------------------------------

    regime_r, regime_m = calculate_metrics(

        subset[
            "imd_rainfall"
        ],

        subset[
            "regime_specific_xgb_rainfall"
        ]
    )


    # --------------------------------------------------------
    # Improvements
    # --------------------------------------------------------

    generic_rmse_improvement = (

        (
            raw_r
            - generic_r
        )
        / raw_r
        * 100
    )


    regime_rmse_improvement = (

        (
            raw_r
            - regime_r
        )
        / raw_r
        * 100
    )


    # --------------------------------------------------------
    # Store
    # --------------------------------------------------------

    regime_results.append({

        "regime": regime,

        "samples": len(subset),

        "raw_rmse": raw_r,

        "generic_xgb_rmse": generic_r,

        "regime_specific_xgb_rmse": regime_r,

        "generic_rmse_improvement_percent":
            generic_rmse_improvement,

        "regime_specific_rmse_improvement_percent":
            regime_rmse_improvement,

        "raw_mae": raw_m,

        "generic_xgb_mae": generic_m,

        "regime_specific_xgb_mae": regime_m
    })


# ============================================================
# REGIME RESULTS DATAFRAME
# ============================================================

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
# SAVE RESULTS
# ============================================================

comparison_df.to_csv(

    OUTPUT_COMPARISON,

    index=False
)


regime_results_df.to_csv(

    OUTPUT_REGIME_RESULTS,

    index=False
)


test_results.to_csv(

    OUTPUT_PREDICTIONS,

    index=False
)


# ============================================================
# SAVE GENERIC MODEL
# ============================================================

generic_model.save_model(

    "data/processed/"
    "generic_xgboost_bias_correction.json"
)


# ============================================================
# SAVE REGIME-SPECIFIC MODELS
# ============================================================

MODEL_DIRECTORY = (
    "data/processed/regime_models"
)


os.makedirs(
    MODEL_DIRECTORY,
    exist_ok=True
)


for regime, model in regime_models.items():

    safe_name = (
        regime
        .replace(" ", "_")
        .replace("/", "_")
    )


    model_path = os.path.join(

        MODEL_DIRECTORY,

        f"{safe_name}_xgboost.json"
    )


    model.save_model(
        model_path
    )


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 70)

print(
    "FINISHED"
)

print("=" * 70)


print("\nSaved:")

print(
    OUTPUT_COMPARISON
)

print(
    OUTPUT_REGIME_RESULTS
)

print(
    OUTPUT_PREDICTIONS
)

print(
    "data/processed/"
    "generic_xgboost_bias_correction.json"
)

print(
    "data/processed/regime_models/"
)


print("\nDone.")