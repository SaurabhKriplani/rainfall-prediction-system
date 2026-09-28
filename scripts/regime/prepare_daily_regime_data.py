import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "regime_features_july_2024.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "daily_regime_features_july_2024.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading regime-feature dataset...")

df = pd.read_csv(INPUT_FILE)
df["date"] = pd.to_datetime(df["date"])


# ============================================================
# CREATE DAILY ATMOSPHERIC DATASET
# ============================================================

features = [
    "mean_wind850",
    "mean_wind700",
    "mean_wind500",

    "mean_rh850",
    "mean_rh700",
    "mean_rh500",

    "mean_rh_lower_mid",

    "mean_upward850",
    "mean_upward700",
    "mean_upward500",

    "mean_shear850_500",

    "mean_t850",
    "mean_t700",
    "mean_t500",
]


daily = (
    df.groupby("date")[features]
    .first()
    .reset_index()
)


# ============================================================
# CHECK
# ============================================================

print("\nDaily dataset shape:")
print(daily.shape)

print("\nMissing values:")
print(daily[features].isna().sum().sum())


# ============================================================
# STANDARDIZE FEATURES
# ============================================================

scaler = StandardScaler()

daily_scaled = scaler.fit_transform(
    daily[features]
)

scaled_columns = [
    feature + "_z"
    for feature in features
]

scaled_df = pd.DataFrame(
    daily_scaled,
    columns=scaled_columns
)


# ============================================================
# COMBINE
# ============================================================

daily_final = pd.concat(
    [
        daily[["date"]],
        daily[features],
        scaled_df
    ],
    axis=1
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

daily_final.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# OUTPUT
# ============================================================

print("\n========================================")
print("DAILY REGIME DATA PREPARED")
print("========================================")

print(f"Output: {OUTPUT_FILE}")
print(f"Shape: {daily_final.shape}")

print("\nDates:")
print(
    daily_final["date"]
    .dt.strftime("%Y-%m-%d")
    .to_list()
)

print("\nDaily atmospheric features:")
print(
    daily_final[
        ["date"] + features
    ].round(3).to_string(index=False)
)