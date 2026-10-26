"""cprics/evaluate.py — backtest early warning against the incumbent.

For a site that eventually reaches an action amplitude, find the earliest
inspection at which C-PRICS's reset-aware trend already forecasts that crossing.
The gap to the actual crossing is the lead time — the advance notice the
incumbent, which only reports at the crossing itself, does not give.
"""
import pandas as pd
from .series import site_trajectory, current_segment
from .predict import forecast_crossing
from .series import site_trajectory, current_segment, detect_resets

def first_crossing(traj, threshold):
    hit = traj[traj["amplitude"] >= threshold]
    return hit["date"].iloc[0] if len(hit) else None


def early_warning_date(traj, threshold, horizon_days=180, drop_fraction=0.30):
    """Earliest inspection whose forecast of the crossing actually holds
    (no reset between the alarm and the real crossing)."""
    actual = first_crossing(traj, threshold)
    if actual is None:
        return None, None
    before = traj[traj["date"] < actual].reset_index(drop=True)
    for k in range(2, len(before) + 1):
        upto = before.iloc[:k]
        seg = current_segment(upto, drop_fraction)
        if len(seg) < 2:
            continue
        pred = forecast_crossing(seg, threshold)
        made_on = upto["date"].iloc[-1]
        if pred is None or not (made_on < pred <= made_on + pd.Timedelta(days=horizon_days)):
            continue
        # valid only if the site keeps rising to the crossing with no tamp in between
        after = traj[(traj["date"] >= made_on) & (traj["date"] <= actual)]
        if detect_resets(after["amplitude"].values, drop_fraction):
            continue
        return made_on, actual
    return None, actual

def lead_time_table(cyc, threshold, horizon_days=180, drop_fraction=0.30):
    """Lead time for every site that reaches `threshold`."""
    rows = []
    for site_id in cyc["site_id"].unique():
        traj = site_trajectory(cyc, site_id)
        if traj["amplitude"].max() < threshold:
            continue
        alarm, actual = early_warning_date(traj, threshold, horizon_days, drop_fraction)
        rows.append({
            "site_id": site_id,
            "actual_crossing": actual,
            "alarm_date": alarm,
            "lead_days": (actual - alarm).days if alarm is not None else None,
        })
    return pd.DataFrame(rows)
