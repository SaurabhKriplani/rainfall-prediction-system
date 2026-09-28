import pandas as pd
import os


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = "data/processed/final_regime_features_july_2024.csv"

OUTPUT_DIR = "data/processed"

TRAIN_FILE = f"{OUTPUT_DIR}/train_july_2024.csv"
VAL_FILE = f"{OUTPUT_DIR}/val_july_2024.csv"
TEST_FILE = f"{OUTPUT_DIR}/test_july_2024.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("LOADING FINAL REGIME DATA")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

print("Full dataset shape:", df.shape)

print("\nDate range:")
print(df["date"].min())
print(df["date"].max())


# ============================================================
# CHECK REQUIRED GEOGRAPHIC FEATURES
# ============================================================

required_geo_features = [
    "elevation",
    "coast_distance_km",
    "slope"
]

print("\nChecking geographic features...")

for feature in required_geo_features:

    if feature not in df.columns:
        raise ValueError(
            f"Missing required geographic feature: {feature}"
        )

    print(
        f"{feature}: "
        f"min={df[feature].min():.3f}, "
        f"max={df[feature].max():.3f}, "
        f"missing={df[feature].isna().sum()}"
    )


# ============================================================
# CHECK DUPLICATES
# ============================================================

duplicate_count = df.duplicated(
    subset=[
        "date",
        "latitude",
        "longitude"
    ]
).sum()

print("\nDuplicate date/grid records:", duplicate_count)

if duplicate_count > 0:
    raise ValueError(
        "Duplicate date/latitude/longitude records found."
    )


# ============================================================
# CHRONOLOGICAL SPLIT
# ============================================================

# July 1-21  -> Training
# July 22-26 -> Validation
# July 27-31 -> Test

train = df[
    df["date"] <= "2024-07-21"
].copy()

val = df[
    (df["date"] >= "2024-07-22") &
    (df["date"] <= "2024-07-26")
].copy()

test = df[
    df["date"] >= "2024-07-27"
].copy()


# ============================================================
# SORT DATA
# ============================================================

sort_columns = [
    "date",
    "latitude",
    "longitude"
]

train = train.sort_values(sort_columns).reset_index(drop=True)

val = val.sort_values(sort_columns).reset_index(drop=True)

test = test.sort_values(sort_columns).reset_index(drop=True)


# ============================================================
# PRINT SPLIT INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("DATA SPLIT")
print("=" * 70)

print("\nTRAIN")
print("Rows:", len(train))
print("Date:", train["date"].min(), "to", train["date"].max())

print("\nVALIDATION")
print("Rows:", len(val))
print("Date:", val["date"].min(), "to", val["date"].max())

print("\nTEST")
print("Rows:", len(test))
print("Date:", test["date"].min(), "to", test["date"].max())


# ============================================================
# REGIME DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("REGIME DISTRIBUTION")
print("=" * 70)

for name, data in [
    ("TRAIN", train),
    ("VALIDATION", val),
    ("TEST", test)
]:

    print(f"\n{name}")

    print(
        data["synoptic_regime"]
        .value_counts()
        .sort_index()
    )


# ============================================================
# SAVE
# ============================================================

train.to_csv(
    TRAIN_FILE,
    index=False
)

val.to_csv(
    VAL_FILE,
    index=False
)

test.to_csv(
    TEST_FILE,
    index=False
)


# ============================================================
# VERIFY SAVED FILES
# ============================================================

print("\n" + "=" * 70)
print("VERIFYING SAVED FILES")
print("=" * 70)

for name, file in [
    ("Train", TRAIN_FILE),
    ("Validation", VAL_FILE),
    ("Test", TEST_FILE)
]:

    check = pd.read_csv(file)

    print(
        f"{name}: {check.shape}"
    )

    for feature in required_geo_features:

        if feature not in check.columns:

            raise ValueError(
                f"{feature} missing from {name} file!"
            )


print("\nGeographic features successfully preserved.")

print("\nFiles saved:")

print(TRAIN_FILE)
print(VAL_FILE)
print(TEST_FILE)

print("\nDone.")