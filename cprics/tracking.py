"""cprics/tracking.py — link islands across dates into tracked sites.

Sites reproduce to ~0.35 m run-to-run and distinct cyclic tops are far apart,
so islands within a section whose centres are within `max_center_gap` metres
are treated as the same site over time.
"""
import numpy as np
import pandas as pd


def track_islands(islands, max_center_gap=7.0):
    """Assign a stable `site_id` to islands of the same location over time."""
    islands = islands.sort_values(["ELR", "TrackID", "center_location"]).copy()
    out, base = [], 0
    for (elr, track), grp in islands.groupby(["ELR", "TrackID"], sort=False):
        grp = grp.copy()
        centers = grp["center_location"].to_numpy()
        local = np.concatenate([[0], (np.diff(centers) > max_center_gap).cumsum()]) \
            if len(centers) > 1 else np.array([0])
        grp["site_id"] = [f"{elr}_{track}_9R_{base + int(n)}" for n in local]
        base += int(local.max()) + 1
        out.append(grp)
    return pd.concat(out).sort_values(["site_id", "date"]).reset_index(drop=True)
