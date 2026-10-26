"""cprics/classify.py — hierarchical clustering of sites into fault archetypes.

Discovery step: run once, inspect the dendrogram, fix a small set of archetypes.
Deterministic — same data, same result.
"""
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.preprocessing import StandardScaler

FEATURES = ["current_amp", "mean_amp", "max_amp", "volatility",
            "slope_overall", "slope_current", "n_resets"]


def cluster_sites(feats, n_clusters=4, features=FEATURES):
    X = StandardScaler().fit_transform(feats[features])
    Z = linkage(X, method="ward")
    out = feats.copy()
    out["cluster"] = fcluster(Z, t=n_clusters, criterion="maxclust")
    return out, Z


def describe_clusters(clustered, features=FEATURES):
    return clustered.groupby("cluster")[features + ["n_obs"]].mean().round(2)


ACTIVE_FEATURES = ["current_amp", "slope_overall", "volatility", "n_resets"]
CONCERN_MM = 18.0


def freeze_archetypes(clustered, names, features=ACTIVE_FEATURES):
    """Store scaler stats + named centroids so new sites can be assigned."""
    scaler = StandardScaler().fit(clustered[features])
    X = scaler.transform(clustered[features])
    centroids = {names[c]: X[clustered["cluster"].values == c].mean(axis=0).tolist()
                 for c in np.unique(clustered["cluster"])}
    return {"features": features, "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist(), "centroids": centroids}


def assign_archetype(feats_df, frozen, cont_max_col="cont_max", concern=CONCERN_MM):
    """Dormant by rule (below concern), else nearest frozen centroid."""
    f = frozen["features"]
    X = (feats_df[f].to_numpy() - np.array(frozen["mean"])) / np.array(frozen["scale"])
    names = list(frozen["centroids"])
    C = np.array([frozen["centroids"][n] for n in names])
    out = []
    for i, row in enumerate(X):
        if feats_df.iloc[i][cont_max_col] < concern:
            out.append("Dormant")
        else:
            out.append(names[int(((C - row) ** 2).sum(axis=1).argmin())])
    return out
