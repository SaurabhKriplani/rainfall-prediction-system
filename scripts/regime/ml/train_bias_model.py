import pandas as pd
import numpy as np

from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error


# ============================================================
# 1. LOAD DATA
# ============================================================

INPUT = "data/final/master_regime_final_jul_sep_2024.csv"

df = pd.read_csv(INPUT)

df["date"] = pd.to_datetime(df["date"])

print("Dataset:", df.shape)
print("Date:", df["date"].min(), "→", df["date"].max())


# ============================================================
# 2. FEATURES
# ============================================================

features = [
    "gfs_rain_24h",
    "latitude",
    "longitude",

    "r500", "r700", "r850",
    "t500", "t700", "t850",

    "u500", "u700", "u850",
    "v500", "v700", "v850",

    "w500", "w700", "w850",
    "z500", "z700", "z850",

    "regime_id_final"
]

target = "bias"


# ============================================================
# 3. TIME-BASED TRAIN / TEST SPLIT
# ============================================================

# July + August = training
# September = testing

train = df[df["date"] < "2024-09-01"].copy()
test = df[df["date"] >= "2024-09-01"].copy()

print("\nTRAINING:", train.shape)
print("TESTING :", test.shape)

print("\nTraining dates:")
print(train["date"].min(), "→", train["date"].max())

print("\nTesting dates:")
print(test["date"].min(), "→", test["date"].max())


X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]


# ============================================================
# 4. TRAIN XGBOOST
# ============================================================

print("\nTraining XGBoost...")

model = XGBRegressor(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Training complete.")


# ============================================================
# 5. PREDICT BIAS
# ============================================================

predicted_bias = model.predict(X_test)

test["predicted_bias"] = predicted_bias


# ============================================================
# 6. CORRECTED RAINFALL
# ============================================================

test["corrected_rainfall"] = (
    test["gfs_rain_24h"] +
    test["predicted_bias"]
)

# Rainfall cannot be negative
test["corrected_rainfall"] = test["corrected_rainfall"].clip(lower=0)


# ============================================================
# 7. RAW GFS ERROR
# ============================================================

raw_rmse = np.sqrt(
    mean_squared_error(
        test["imd_rainfall"],
        test["gfs_rain_24h"]
    )
)

raw_mae = mean_absolute_error(
    test["imd_rainfall"],
    test["gfs_rain_24h"]
)


# ============================================================
# 8. CORRECTED ERROR
# ============================================================

corrected_rmse = np.sqrt(
    mean_squared_error(
        test["imd_rainfall"],
        test["corrected_rainfall"]
    )
)

corrected_mae = mean_absolute_error(
    test["imd_rainfall"],
    test["corrected_rainfall"]
)


# ============================================================
# 9. RESULTS
# ============================================================

print("\n====================================")
print("BIAS CORRECTION RESULTS")
print("====================================")

print(f"Raw GFS RMSE       : {raw_rmse:.4f}")
print(f"Corrected RMSE     : {corrected_rmse:.4f}")

print(f"\nRaw GFS MAE        : {raw_mae:.4f}")
print(f"Corrected MAE      : {corrected_mae:.4f}")

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

print(f"\nRMSE improvement   : {rmse_improvement:.2f}%")
print(f"MAE improvement    : {mae_improvement:.2f}%")


# ============================================================
# 10. SAVE RESULTS
# ============================================================

OUTPUT = "data/final/bias_corrected_sep_2024.csv"

test.to_csv(
    OUTPUT,
    index=False
)

print("\nSaved:")
print(OUTPUT)


# ============================================================
# 11. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print("\nTOP FEATURES")
print("============")

print(importance.head(15).to_string(index=False))

importance.to_csv(
    "data/final/bias_model_feature_importance.csv",
    index=False
)

print("\nFeature importance saved.")