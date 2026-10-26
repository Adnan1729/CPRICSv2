"""cprics/risk.py — a transparent risk score per island observation.

risk = how bad now (severity) blended with how fast it's rising (growth).
Both 0-1, so the score is 0-1 and reads off by hand. Parameters are here,
in the open, to tune.
"""
import numpy as np
from .series import current_segment
from .predict import fit_linear_trend

FLOOR_MM     = 12.0   # a just-formed island (3 peaks x 5mm x 0.8)
ACTION_MM    = 30.0   # category I (immediate action)
GROWTH_FULL  = 2.0    # mm per 28 days that counts as 'fast' (urgency = 1)
W_SEVERITY   = 0.6    # weight on how-bad-now vs how-fast-rising
W_GROWTH     = 0.4


def severity(amp):
    """How far the site has climbed from a just-formed island toward action."""
    return float(np.clip((amp - FLOOR_MM) / (ACTION_MM - FLOOR_MM), 0, 1))


def growth_urgency(traj):
    """0-1 from the current segment's (reset-aware) slope."""
    seg = current_segment(traj)
    fit = fit_linear_trend(seg["date"], seg["amplitude"])
    if fit is None:
        return 0.0
    slope_per_28d = fit[0] * 28
    return float(np.clip(slope_per_28d / GROWTH_FULL, 0, 1))


def risk_score(traj):
    """Risk for a site given its trajectory up to now (last point = current)."""
    amp_now = traj["amplitude"].iloc[-1]
    return W_SEVERITY * severity(amp_now) + W_GROWTH * growth_urgency(traj)
