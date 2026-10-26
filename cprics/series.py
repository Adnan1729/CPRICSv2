"""cprics/series.py — per-site trajectories and maintenance-reset detection.

A 'reset' is a large drop in amplitude between inspections (most likely a tamp).
For trend/forecasting we use only the current growth segment, since the last
reset; earlier segments are kept for context but excluded from the trend.
"""
import numpy as np


# def site_trajectory(cyc, site_id):
#     """One site's (date, amplitude) history, sorted, one row per date."""
#     s = cyc[cyc["site_id"] == site_id]
#     s = (s.groupby("date", as_index=False)
#            .agg(amplitude=("amplitude", "max"),      # worst reading on that date
#                 category=("category", "last"),
#                 threshold=("threshold", "last"))
#            .sort_values("date")
#            .reset_index(drop=True))
#     return s

def site_trajectory(data, site_id):
    """One site's (date, amplitude) history, sorted, one row per date (worst reading)."""
    s = data[data["site_id"] == site_id]
    return (s.groupby("date", as_index=False)["amplitude"].max()
             .sort_values("date").reset_index(drop=True))


def detect_resets(amplitudes, drop_fraction=0.30):
    """Positions where amplitude fell by more than `drop_fraction` of the prior value."""
    amps = np.asarray(amplitudes, dtype=float)
    return [i for i in range(1, len(amps))
            if amps[i] < (1 - drop_fraction) * amps[i - 1]]


def current_segment(traj, drop_fraction=0.30):
    """The slice of a trajectory since its last reset (the current growth)."""
    resets = detect_resets(traj["amplitude"].values, drop_fraction)
    start = resets[-1] if resets else 0
    return traj.iloc[start:].reset_index(drop=True)
