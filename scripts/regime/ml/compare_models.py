import pandas as pd
import numpy as np

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error

from xgboost import XGBRegressor


# ============================================================
# FILES
# ============================================================

TRAIN = "data/processed/train_july_2024.csv"
VAL = "data/processed/val_july_2024.csv"
TEST = "data/processed/test_july_2024.csv"


# ============================================================
# LOAD
# ============================================================

train = pd.read_csv(TRAIN)
val = pd.read_csv(VAL)
test = pd.read_csv(TEST)

print("Train:", train.shape)
print("Validation:", val.shape)
print("Test:", test.shape)


# ============================================================
# FEATURES
# ============================================================

numeric_features = [
    "gfs_rain_24h",

    "z850", "r850", "t850", "u850", "v850", "w850",
    "z700", "r700", "t700", "u700", "v700", "w700",
    "z500", "r500", "t500", "u500", "v500", "w500",

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

    "elevation_m",
    "coast_distance_km",
    "terrain_slope_deg"
]


categorical_features = [
    "synoptic_regime"
]


# ============================================================
# ONE-HOT ENCODE REGIME
# ============================================================

combined = pd.concat(
    [train, val, test],
    axis=0
)

combined = pd.get_dummies(
    combined,
    columns=categorical_features,
    dtype=int
)

train = combined.iloc[:len(train)].copy()
val = combined.iloc[len(train):len(train) + len(val)].copy()
test = combined.iloc[len(train) + len(val):].copy()


regime_columns = [
    c for c in train.columns
    if c.startswith("synoptic_regime_")
]

features = numeric_features + regime_columns

print("\nNumber of features:", len(features))
print("Regime features:", regime_columns)


# ============================================================
# DATA
# ============================================================

X_train = train[features]
X_val = val[features]
X_test = test[features]

y_train = train["bias"]
y_val = val["bias"]
y_test = test["bias"]


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(name, model):

    model.fit(X_train, y_train)

    val_bias = model.predict(X_val)
    test_bias = model.predict(X_test)

    val_corrected = np.maximum(
        val["gfs_rain_24h"].values + val_bias,
        0
    )

    test_corrected = np.maximum(
        test["gfs_rain_24h"].values + test_bias,
        0
    )

    val_rmse = np.sqrt(
        mean_squared_error(
            val["imd_rainfall"],
            val_corrected
        )
    )

    test_rmse = np.sqrt(
        mean_squared_error(
            test["imd_rainfall"],
            test_corrected
        )
    )

    val_mae = mean_absolute_error(
        val["imd_rainfall"],
        val_corrected
    )

    test_mae = mean_absolute_error(
        test["imd_rainfall"],
        test_corrected
    )

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    print(f"Validation RMSE: {val_rmse:.4f}")
    print(f"Validation MAE : {val_mae:.4f}")

    print(f"Test RMSE      : {test_rmse:.4f}")
    print(f"Test MAE       : {test_mae:.4f}")

    return {
        "model": name,
        "val_rmse": val_rmse,
        "val_mae": val_mae,
        "test_rmse": test_rmse,
        "test_mae": test_mae
    }


# ============================================================
# RAW GFS BASELINE
# ============================================================

raw_val_rmse = np.sqrt(
    mean_squared_error(
        val["imd_rainfall"],
        val["gfs_rain_24h"]
    )
)

raw_test_rmse = np.sqrt(
    mean_squared_error(
        test["imd_rainfall"],
        test["gfs_rain_24h"]
    )
)

raw_val_mae = mean_absolute_error(
    val["imd_rainfall"],
    val["gfs_rain_24h"]
)

raw_test_mae = mean_absolute_error(
    test["imd_rainfall"],
    test["gfs_rain_24h"]
)

results = [{
    "model": "Raw GFS",
    "val_rmse": raw_val_rmse,
    "val_mae": raw_val_mae,
    "test_rmse": raw_test_rmse,
    "test_mae": raw_test_mae
}]


# ============================================================
# RIDGE
# ============================================================

ridge = Pipeline([
    ("scaler", StandardScaler()),
    ("model", Ridge(alpha=10.0))
])

results.append(
    evaluate_model(
        "Ridge Regression",
        ridge
    )
)


# ============================================================
# RANDOM FOREST
# ============================================================

rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    min_samples_leaf=10,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1
)

results.append(
    evaluate_model(
        "Random Forest",
        rf
    )
)


# ============================================================
# XGBOOST
# ============================================================

xgb = XGBRegressor(
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

results.append(
    evaluate_model(
        "XGBoost",
        xgb
    )
)


# ============================================================
# RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(results)

print("\n\n")
print("=" * 80)
print("FINAL MODEL COMPARISON")
print("=" * 80)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    "data/processed/model_comparison_results.csv",
    index=False
)

print(
    "\nSaved:"
    "\ndata/processed/model_comparison_results.csv"
)