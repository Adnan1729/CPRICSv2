"""cprics/features.py — interpretable shape features per tracked site.

Each site's accumulated-amplitude trajectory is summarised by a few readable
numbers describing its behaviour, for clustering into fault archetypes.
"""
import pandas as pd
from .series import site_trajectory, detect_resets, current_segment
from .predict import fit_linear_trend


def site_features(isl, site_id):
    traj = site_trajectory(isl, site_id)
    amps = traj["amplitude"].to_numpy()
    fit_all = fit_linear_trend(traj["date"], amps)
    seg = current_segment(traj)
    fit_cur = fit_linear_trend(seg["date"], seg["amplitude"])
    return {
        "site_id": site_id,
        "n_obs": len(traj),
        "current_amp": amps[-1],
        "mean_amp": amps.mean(),
        "max_amp": amps.max(),
        "volatility": amps.std() if len(amps) > 1 else 0.0,
        "slope_overall": fit_all[0] * 28 if fit_all else 0.0,   # mm per 28 days
        "slope_current": fit_cur[0] * 28 if fit_cur else 0.0,
        "n_resets": len(detect_resets(amps)),
    }


def build_feature_table(isl, min_obs=3):
    feats = pd.DataFrame(site_features(isl, s) for s in isl["site_id"].unique())
    return feats[feats["n_obs"] >= min_obs].reset_index(drop=True)
