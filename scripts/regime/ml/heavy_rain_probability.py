import pandas as pd
import numpy as np

from xgboost import XGBClassifier
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    confusion_matrix
)

# ============================================================
# 1. LOAD DATA
# ============================================================

INPUT = "data/final/master_regime_final_jul_sep_2024.csv"
OUTPUT = "data/final/heavy_rain_probability_sep_2024.csv"

df = pd.read_csv(INPUT)
df["date"] = pd.to_datetime(df["date"])

print("Dataset:", df.shape)


# ============================================================
# 2. CREATE HEAVY RAINFALL TARGET
# ============================================================

THRESHOLD = 64.5

df["heavy_rain"] = (
    df["imd_rainfall"] >= THRESHOLD
).astype(int)

print("\nHeavy rainfall samples:")
print(df["heavy_rain"].value_counts())

print("\nHeavy rainfall percentage:")
print(df["heavy_rain"].mean() * 100)


# ============================================================
# 3. FEATURES
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

X = df[features]
y = df["heavy_rain"]


# ============================================================
# 4. TIME-BASED SPLIT
# ============================================================

train = df[df["date"] < "2024-09-01"].copy()
test = df[df["date"] >= "2024-09-01"].copy()

X_train = train[features]
y_train = train["heavy_rain"]

X_test = test[features]
y_test = test["heavy_rain"]

print("\nTraining:", X_train.shape)
print("Testing :", X_test.shape)

print(
    "Train heavy events:",
    y_train.sum()
)

print(
    "Test heavy events:",
    y_test.sum()
)


# ============================================================
# 5. HANDLE CLASS IMBALANCE
# ============================================================

positive = y_train.sum()
negative = len(y_train) - positive

scale_pos_weight = negative / positive

print(
    "\nScale positive weight:",
    scale_pos_weight
)


# ============================================================
# 6. TRAIN CLASSIFIER
# ============================================================

print("\nTraining heavy-rainfall classifier...")

model = XGBClassifier(
    n_estimators=300,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,

    objective="binary:logistic",

    scale_pos_weight=scale_pos_weight,

    eval_metric="logloss",

    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Training complete.")


# ============================================================
# 7. PREDICT PROBABILITY
# ============================================================

probability = model.predict_proba(X_test)[:, 1]

test["heavy_rain_probability"] = probability


# ============================================================
# 8. AUC
# ============================================================

auc = roc_auc_score(
    y_test,
    probability
)

print("\n======================================")
print("HEAVY RAINFALL PROBABILITY")
print("======================================")

print(f"ROC-AUC: {auc:.4f}")


# ============================================================
# 9. USE 50% PROBABILITY THRESHOLD
# ============================================================

predicted = (
    probability >= 0.50
).astype(int)

precision = precision_score(
    y_test,
    predicted,
    zero_division=0
)

pod = recall_score(
    y_test,
    predicted,
    zero_division=0
)

cm = confusion_matrix(
    y_test,
    predicted
)

tn, fp, fn, tp = cm.ravel()

far = (
    fp / (tp + fp)
    if (tp + fp) > 0
    else 0
)

csi = (
    tp / (tp + fp + fn)
    if (tp + fp + fn) > 0
    else 0
)


print("\nUsing probability threshold = 0.50")

print(f"Precision : {precision:.4f}")
print(f"POD       : {pod:.4f}")
print(f"FAR       : {far:.4f}")
print(f"CSI       : {csi:.4f}")

print("\nConfusion matrix:")
print(cm)


# ============================================================
# 10. SAVE
# ============================================================

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

importance.to_csv(
    "data/final/heavy_rain_feature_importance.csv",
    index=False
)

print("\nTop features:")
print(
    importance.head(15).to_string(index=False)
)