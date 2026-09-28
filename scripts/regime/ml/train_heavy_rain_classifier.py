# scripts/regime/ml/train_heavy_rain_classifier.py

import os
import json
import numpy as np
import pandas as pd

from xgboost import XGBClassifier
from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# 1. PATHS
# ============================================================

TRAIN_FILE = "data/processed/train_july_2024.csv"
VAL_FILE = "data/processed/val_july_2024.csv"
TEST_FILE = "data/processed/test_july_2024.csv"

OUTPUT_DIR = "data/processed"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

train = pd.read_csv(TRAIN_FILE)
val = pd.read_csv(VAL_FILE)
test = pd.read_csv(TEST_FILE)

print("Train shape:", train.shape)
print("Validation shape:", val.shape)
print("Test shape:", test.shape)


# ============================================================
# 3. HEAVY RAINFALL THRESHOLD
# ============================================================

# IMD heavy rainfall threshold
HEAVY_THRESHOLD = 64.5

print("\nHeavy rainfall threshold:", HEAVY_THRESHOLD, "mm/day")


# ============================================================
# 4. CREATE TARGET
# ============================================================

train["heavy_rain"] = (
    train["imd_rainfall"] >= HEAVY_THRESHOLD
).astype(int)

val["heavy_rain"] = (
    val["imd_rainfall"] >= HEAVY_THRESHOLD
).astype(int)

test["heavy_rain"] = (
    test["imd_rainfall"] >= HEAVY_THRESHOLD
).astype(int)


# ============================================================
# 5. SHOW CLASS DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("CLASS DISTRIBUTION")
print("=" * 70)

for name, df in [
    ("Train", train),
    ("Validation", val),
    ("Test", test)
]:

    counts = df["heavy_rain"].value_counts().sort_index()

    non_heavy = counts.get(0, 0)
    heavy = counts.get(1, 0)

    total = len(df)

    print(f"\n{name}")
    print(f"  Non-heavy : {non_heavy:,} ({non_heavy / total * 100:.2f}%)")
    print(f"  Heavy     : {heavy:,} ({heavy / total * 100:.2f}%)")


# ============================================================
# 6. FEATURE SELECTION
# ============================================================

# Atmospheric / rainfall features
numeric_features = [
    "gfs_rain_24h",

    "z850",
    "r850",
    "t850",
    "u850",
    "v850",
    "w850",

    "z700",
    "r700",
    "t700",
    "u700",
    "v700",
    "w700",

    "z500",
    "r500",
    "t500",
    "u500",
    "v500",
    "w500",

    # Derived regime features
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
    "elevation",
    "coast_distance_km",
    "slope"
]


# ============================================================
# 7. REGIME ONE-HOT ENCODING
# ============================================================

# Make sure regime columns exist
for df in [train, val, test]:

    df["regime_background_monsoon"] = (
        df["synoptic_regime"] == "background_monsoon"
    ).astype(int)

    df["regime_low_pressure"] = (
        df["synoptic_regime"] == "low_pressure"
    ).astype(int)

    df["regime_depression"] = (
        df["synoptic_regime"] == "depression"
    ).astype(int)


regime_features = [
    "regime_background_monsoon",
    "regime_low_pressure",
    "regime_depression"
]


# ============================================================
# 8. FINAL FEATURES
# ============================================================

features = numeric_features + regime_features

print("\n" + "=" * 70)
print("FEATURES")
print("=" * 70)

print("Number of features:", len(features))

for i, feature in enumerate(features, start=1):
    print(f"{i:2d}. {feature}")


# ============================================================
# 9. CHECK MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("CHECKING MISSING VALUES")
print("=" * 70)

for name, df in [
    ("Train", train),
    ("Validation", val),
    ("Test", test)
]:

    missing = df[features].isna().sum().sum()

    print(f"{name} missing feature values:", missing)

    if missing > 0:
        raise ValueError(
            f"{name} contains missing values in model features."
        )


# ============================================================
# 10. CREATE X / Y
# ============================================================

X_train = train[features]
y_train = train["heavy_rain"]

X_val = val[features]
y_val = val["heavy_rain"]

X_test = test[features]
y_test = test["heavy_rain"]


# ============================================================
# 11. CLASS IMBALANCE
# ============================================================

negative_count = int((y_train == 0).sum())
positive_count = int((y_train == 1).sum())

if positive_count == 0:
    raise ValueError("No heavy-rain samples found in training data.")

scale_pos_weight = negative_count / positive_count

print("\n" + "=" * 70)
print("CLASS WEIGHT")
print("=" * 70)

print("Negative samples:", negative_count)
print("Positive samples:", positive_count)
print("scale_pos_weight:", scale_pos_weight)


# ============================================================
# 12. TRAIN XGBOOST CLASSIFIER
# ============================================================

print("\n" + "=" * 70)
print("TRAINING XGBOOST HEAVY RAIN CLASSIFIER")
print("=" * 70)

model = XGBClassifier(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.03,

    min_child_weight=10,

    subsample=0.8,
    colsample_bytree=0.8,

    reg_alpha=0.1,
    reg_lambda=5,

    objective="binary:logistic",

    scale_pos_weight=scale_pos_weight,

    eval_metric="logloss",

    random_state=42,

    n_jobs=-1
)


model.fit(
    X_train,
    y_train,

    eval_set=[
        (X_train, y_train),
        (X_val, y_val)
    ],

    verbose=False
)

print("Training completed.")


# ============================================================
# 13. PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

test_probability = model.predict_proba(X_test)[:, 1]

# Default classification threshold
CLASSIFICATION_THRESHOLD = 0.5

test_prediction = (
    test_probability >= CLASSIFICATION_THRESHOLD
).astype(int)


# ============================================================
# 14. CONFUSION MATRIX
# ============================================================

tn, fp, fn, tp = confusion_matrix(
    y_test,
    test_prediction,
    labels=[0, 1]
).ravel()


# ============================================================
# 15. OVERALL METRICS
# ============================================================

if (tp + fn) > 0:
    pod = tp / (tp + fn)
else:
    pod = np.nan


if (tp + fp) > 0:
    far = fp / (tp + fp)
else:
    far = np.nan


if (tp + fn + fp) > 0:
    csi = tp / (tp + fn + fp)
else:
    csi = np.nan


# ETS
total = tp + tn + fp + fn

if total > 0:

    random_hits = (
        (tp + fp) *
        (tp + fn)
    ) / total

    denominator = (
        tp +
        fn +
        fp -
        random_hits
    )

    if denominator != 0:
        ets = (
            tp - random_hits
        ) / denominator
    else:
        ets = np.nan

else:
    ets = np.nan


precision = precision_score(
    y_test,
    test_prediction,
    zero_division=0
)

recall = recall_score(
    y_test,
    test_prediction,
    zero_division=0
)

f1 = f1_score(
    y_test,
    test_prediction,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    test_probability
)

pr_auc = average_precision_score(
    y_test,
    test_probability
)


# ============================================================
# 16. PRINT OVERALL RESULTS
# ============================================================

print("\n" + "=" * 70)
print("OVERALL TEST RESULTS")
print("=" * 70)

print("\nConfusion Matrix:")
print("-----------------")

print("TN:", tn)
print("FP:", fp)
print("FN:", fn)
print("TP:", tp)

print("\nMeteorological Verification Metrics:")
print("-------------------------------------")

print(f"POD       : {pod:.4f}")
print(f"FAR       : {far:.4f}")
print(f"CSI       : {csi:.4f}")
print(f"ETS       : {ets:.4f}")

print("\nMachine Learning Metrics:")
print("-------------------------")

print(f"Precision  : {precision:.4f}")
print(f"Recall     : {recall:.4f}")
print(f"F1         : {f1:.4f}")
print(f"ROC-AUC    : {roc_auc:.4f}")
print(f"PR-AUC     : {pr_auc:.4f}")


# ============================================================
# 17. REGIME-WISE EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("REGIME-WISE TEST RESULTS")
print("=" * 70)

regime_results = []

# IMPORTANT:
# Use NumPy positional masks here.
# This avoids the pandas "Unalignable boolean Series" error.

for regime in sorted(test["synoptic_regime"].unique()):

    mask = (
        test["synoptic_regime"].values == regime
    )

    observed = y_test.to_numpy()[mask]

    predicted = test_prediction[mask]

    probabilities = test_probability[mask]

    regime_tn, regime_fp, regime_fn, regime_tp = confusion_matrix(
        observed,
        predicted,
        labels=[0, 1]
    ).ravel()


    # POD
    if (regime_tp + regime_fn) > 0:

        regime_pod = (
            regime_tp /
            (regime_tp + regime_fn)
        )

    else:

        regime_pod = np.nan


    # FAR
    if (regime_tp + regime_fp) > 0:

        regime_far = (
            regime_fp /
            (regime_tp + regime_fp)
        )

    else:

        regime_far = np.nan


    # CSI
    if (
        regime_tp +
        regime_fn +
        regime_fp
    ) > 0:

        regime_csi = (
            regime_tp /
            (
                regime_tp +
                regime_fn +
                regime_fp
            )
        )

    else:

        regime_csi = np.nan


    # Precision
    regime_precision = precision_score(
        observed,
        predicted,
        zero_division=0
    )


    # Recall
    regime_recall = recall_score(
        observed,
        predicted,
        zero_division=0
    )


    # F1
    regime_f1 = f1_score(
        observed,
        predicted,
        zero_division=0
    )


    # ROC-AUC only if both classes exist
    if len(np.unique(observed)) == 2:

        regime_roc_auc = roc_auc_score(
            observed,
            probabilities
        )

    else:

        regime_roc_auc = np.nan


    # Store results
    regime_results.append({

        "regime": regime,

        "samples": int(mask.sum()),

        "observed_heavy": int(observed.sum()),

        "predicted_heavy": int(predicted.sum()),

        "TN": int(regime_tn),
        "FP": int(regime_fp),
        "FN": int(regime_fn),
        "TP": int(regime_tp),

        "POD": regime_pod,

        "FAR": regime_far,

        "CSI": regime_csi,

        "Precision": regime_precision,

        "Recall": regime_recall,

        "F1": regime_f1,

        "ROC_AUC": regime_roc_auc
    })


# ============================================================
# 18. DISPLAY REGIME RESULTS
# ============================================================

regime_results_df = pd.DataFrame(
    regime_results
)

print("\n")

print(
    regime_results_df.to_string(
        index=False
    )
)


# ============================================================
# 19. SAVE REGIME RESULTS
# ============================================================

regime_results_file = (
    f"{OUTPUT_DIR}/heavy_rain_regime_results.csv"
)

regime_results_df.to_csv(
    regime_results_file,
    index=False
)

print(
    "\nSaved regime results:",
    regime_results_file
)


# ============================================================
# 20. SAVE TEST PREDICTIONS
# ============================================================

prediction_df = test[
    [
        "date",
        "latitude",
        "longitude",
        "synoptic_regime",
        "gfs_rain_24h",
        "imd_rainfall"
    ]
].copy()

prediction_df["heavy_rain_observed"] = y_test.to_numpy()

prediction_df["heavy_rain_probability"] = (
    test_probability
)

prediction_df["heavy_rain_predicted"] = (
    test_prediction
)


prediction_file = (
    f"{OUTPUT_DIR}/test_heavy_rain_predictions.csv"
)

prediction_df.to_csv(
    prediction_file,
    index=False
)

print(
    "Saved predictions:",
    prediction_file
)


# ============================================================
# 21. SAVE OVERALL METRICS
# ============================================================

overall_results = {

    "heavy_rain_threshold_mm": HEAVY_THRESHOLD,

    "classification_threshold": CLASSIFICATION_THRESHOLD,

    "train_samples": int(len(train)),
    "validation_samples": int(len(val)),
    "test_samples": int(len(test)),

    "train_heavy_samples": int(positive_count),

    "scale_pos_weight": float(scale_pos_weight),

    "TN": int(tn),
    "FP": int(fp),
    "FN": int(fn),
    "TP": int(tp),

    "POD": float(pod),
    "FAR": float(far),
    "CSI": float(csi),
    "ETS": float(ets),

    "Precision": float(precision),
    "Recall": float(recall),
    "F1": float(f1),

    "ROC_AUC": float(roc_auc),
    "PR_AUC": float(pr_auc),

    "number_of_features": len(features),

    "features": features
}


metrics_file = (
    f"{OUTPUT_DIR}/heavy_rain_classifier_results.json"
)


with open(
    metrics_file,
    "w"
) as f:

    json.dump(
        overall_results,
        f,
        indent=4
    )


print(
    "Saved overall metrics:",
    metrics_file
)


# ============================================================
# 22. SAVE MODEL
# ============================================================

model_file = (
    f"{OUTPUT_DIR}/heavy_rain_xgboost.json"
)

model.save_model(
    model_file
)

print(
    "Saved model:",
    model_file
)


# ============================================================
# 23. FEATURE IMPORTANCE
# ============================================================

importance_df = pd.DataFrame({

    "feature": features,

    "importance": model.feature_importances_

})


importance_df = importance_df.sort_values(
    "importance",
    ascending=False
)


importance_file = (
    f"{OUTPUT_DIR}/heavy_rain_feature_importance.csv"
)

importance_df.to_csv(
    importance_file,
    index=False
)


# ============================================================
# 24. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("HEAVY RAIN CLASSIFIER COMPLETED")
print("=" * 70)

print("\nThreshold:", HEAVY_THRESHOLD, "mm/day")

print("\nOverall metrics:")

print(f"  POD      = {pod:.4f}")
print(f"  FAR      = {far:.4f}")
print(f"  CSI      = {csi:.4f}")
print(f"  ETS      = {ets:.4f}")

print(f"\n  Precision = {precision:.4f}")
print(f"  Recall    = {recall:.4f}")
print(f"  F1        = {f1:.4f}")

print(f"\n  ROC-AUC   = {roc_auc:.4f}")
print(f"  PR-AUC    = {pr_auc:.4f}")

print("\nFiles generated:")

print("1.", metrics_file)
print("2.", regime_results_file)
print("3.", prediction_file)
print("4.", model_file)
print("5.", importance_file)

print("\nDone.")