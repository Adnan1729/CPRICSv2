"""cprics/predict.py — fit the current growth trend and forecast a threshold crossing."""
import numpy as np
import pandas as pd


def fit_linear_trend(dates, amplitudes):
    """Fit amplitude = slope*days + intercept. Returns (slope_per_day, intercept, day0)."""
    dates = pd.to_datetime(pd.Series(list(dates)))
    day0 = dates.min()
    days = (dates - day0).dt.days.to_numpy(dtype=float)
    amps = np.asarray(amplitudes, dtype=float)
    if len(days) < 2 or np.ptp(days) == 0:
        return None
    slope, intercept = np.polyfit(days, amps, 1)
    return slope, intercept, day0


def forecast_crossing(traj_segment, threshold):
    """Date the current growth trend crosses `threshold` (mm), or None if not growing."""
    fit = fit_linear_trend(traj_segment["date"], traj_segment["amplitude"])
    if fit is None:
        return None
    slope, intercept, day0 = fit
    if slope <= 0:
        return None
    day_cross = (threshold - intercept) / slope
    return day0 + pd.Timedelta(days=float(day_cross))


def current_slope(traj, min_points=3):
    """Reset-aware slope (mm per 28 days), robust to short segments.
    Needs >=min_points in the current segment; otherwise falls back to the
    overall trend, which uses all the data."""
    from .series import current_segment
    seg = current_segment(traj)
    fit = fit_linear_trend(seg["date"], seg["amplitude"]) if len(seg) >= min_points \
        else fit_linear_trend(traj["date"], traj["amplitude"])
    return fit[0] * 28 if fit else 0.0
