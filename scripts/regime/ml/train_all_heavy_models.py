import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score

INPUT = "data/final/master_regime_final_jul_sep_2024.csv"
OUTPUT = "data/final/heavy_rain_probabilities_sep_2024.csv"

df = pd.read_csv(INPUT)
df["date"] = pd.to_datetime(df["date"])

features = [
    "gfs_rain_24h",
    "latitude", "longitude",
    "r500", "r700", "r850",
    "t500", "t700", "t850",
    "u500", "u700", "u850",
    "v500", "v700", "v850",
    "w500", "w700", "w850",
    "z500", "z700", "z850",
    "regime_id_final"
]

train = df[df["date"] < "2024-09-01"].copy()
test = df[df["date"] >= "2024-09-01"].copy()

X_train = train[features]
X_test = test[features]

thresholds = [
    (64.5, "heavy"),
    (115.6, "very_heavy"),
    (204.5, "extremely_heavy")
]

results = test[
    ["date", "latitude", "longitude",
     "gfs_rain_24h", "imd_rainfall",
     "regime_final", "regime_id_final"]
].copy()

for threshold, name in thresholds:

    print(f"\n{'='*50}")
    print(f"{name.upper()} >= {threshold} mm")
    print(f"{'='*50}")

    y_train = (
        train["imd_rainfall"] >= threshold
    ).astype(int)

    y_test = (
        test["imd_rainfall"] >= threshold
    ).astype(int)

    positive = y_train.sum()
    negative = len(y_train) - positive

    print("Training events:", positive)
    print("Testing events :", y_test.sum())

    if positive == 0:
        print("No training events. Skipping.")
        results[f"{name}_probability"] = 0.0
        continue

    weight = negative / positive

    model = XGBClassifier(
        n_estimators=300,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        scale_pos_weight=weight,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    probability = model.predict_proba(X_test)[:, 1]

    results[f"{name}_probability"] = probability

    if y_test.sum() > 0:
        auc = roc_auc_score(y_test, probability)
        print(f"ROC-AUC: {auc:.4f}")

    print(
        f"Max probability: {probability.max():.4f}"
    )


results.to_csv(OUTPUT, index=False)

print("\n======================================")
print("ALL PROBABILITY MODELS COMPLETE")
print("======================================")

print("\nSaved:")
print(OUTPUT)

print("\nColumns:")
print(results.columns.tolist())