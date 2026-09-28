import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "daily_regime_features_july_2024.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "daily_regime_clusters_july_2024.csv"
)


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])


# ============================================================
# FEATURES
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


X = df[features].copy()


# ============================================================
# STANDARDIZE
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ============================================================
# TEST DIFFERENT K VALUES
# ============================================================

print("========================================")
print("TESTING CLUSTER COUNTS")
print("========================================")

scores = {}

for k in [3, 4, 5]:

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=20
    )

    labels = model.fit_predict(X_scaled)

    score = silhouette_score(
        X_scaled,
        labels
    )

    scores[k] = score

    print(
        f"K = {k} | "
        f"Silhouette Score = {score:.4f}"
    )


# ============================================================
# SELECT BEST K
# ============================================================

best_k = max(
    scores,
    key=scores.get
)

print("\n========================================")
print(f"Selected K = {best_k}")
print("========================================")


# ============================================================
# FINAL MODEL
# ============================================================

model = KMeans(
    n_clusters=best_k,
    random_state=42,
    n_init=20
)

df["cluster"] = model.fit_predict(X_scaled)


# ============================================================
# SORT CLUSTERS BY DATE
# ============================================================

df = df.sort_values("date").reset_index(drop=True)


# ============================================================
# PRINT CLUSTER MEMBERS
# ============================================================

print("\nCluster assignment by date:\n")

for cluster in sorted(df["cluster"].unique()):

    dates = df.loc[
        df["cluster"] == cluster,
        "date"
    ].dt.strftime("%Y-%m-%d").tolist()

    print(f"Cluster {cluster}:")
    print(", ".join(dates))
    print()


# ============================================================
# CLUSTER CHARACTERISTICS
# ============================================================

print("========================================")
print("CLUSTER CHARACTERISTICS")
print("========================================")

cluster_summary = (
    df.groupby("cluster")[features]
    .mean()
    .round(3)
)

print(cluster_summary.to_string())


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n========================================")
print("CLUSTERING COMPLETE")
print("========================================")

print(f"Output: {OUTPUT_FILE}")
print(f"Shape: {df.shape}")