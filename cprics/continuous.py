"""cprics/continuous.py — the continuous pre-risk measure.

Replaces the incumbent's hard 5 mm cutoff with a smooth sigmoid weight, so a
cyclic top grows gradually as its peaks rise instead of jumping the instant a
peak crosses 5 mm. This is the 'Continuous' in C-PRICS, and it's what the
2024 sigmoid was meant to do.
"""
import numpy as np
import pandas as pd

CANDIDATE_FLOOR = 2.0   # mm; ignore pure noise below this (peak locations stay stable)
SIG_CENTRE      = 5.0   # mm; the incumbent's threshold, now the sigmoid's midpoint
SIG_WIDTH       = 1.0   # mm; how sharply the weight turns on (smaller -> closer to a cliff)
GAP_FACTOR      = 1.5
UP_MULTIPLIER   = 0.8


def soft_weight(peak, centre=SIG_CENTRE, width=SIG_WIDTH):
    return 1.0 / (1.0 + np.exp(-(peak - centre) / width))


def find_islands_continuous(peaks, wavelength, candidate_floor=CANDIDATE_FLOOR,
                            gap_factor=GAP_FACTOR):
    """Group wavelength-spaced peaks (above a low floor) and accumulate with a
    smooth sigmoid weight — no hard 5 mm cutoff, no hard >=3 count."""
    cand = (peaks[peaks["amplitude"] >= candidate_floor]
            .sort_values("Location_m").reset_index(drop=True))
    if cand.empty:
        return pd.DataFrame()
    group = (cand["Location_m"].diff() > gap_factor * wavelength).cumsum()
    out = []
    for _, g in cand.groupby(group):
        amp = g["amplitude"].to_numpy()
        w = soft_weight(amp)
        out.append({
            "start_location": g["Location_m"].iloc[0],
            "end_location": g["Location_m"].iloc[-1],
            "center_location": g["Location_m"].mean(),
            "n_candidate_peaks": len(g),
            "effective_peaks": float(w.sum()),            # smooth 'count'
            "amplitude": UP_MULTIPLIER * float((amp * w).sum()),
        })
    return pd.DataFrame(out)


def build_all_continuous(peaks, wavelength, **kw):
    out = []
    for (elr, track, date), g in peaks.groupby(["ELR", "TrackID", "date"]):
        isl = find_islands_continuous(g, wavelength, **kw)
        if not isl.empty:
            isl["ELR"], isl["TrackID"], isl["date"] = elr, track, date
            out.append(isl)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()

def _hard_amplitude(locs, amps, wavelength, gap_factor):
    """Incumbent amplitude from the strong (>=5 mm) peaks among these."""
    strong = amps >= SIG_CENTRE
    if strong.sum() < 3:
        return 0.0
    sl, sa = locs[strong], amps[strong]
    order = np.argsort(sl); sl, sa = sl[order], sa[order]
    grp = np.concatenate([[0], (np.diff(sl) > gap_factor * wavelength).cumsum()])
    return sum(UP_MULTIPLIER * sa[grp == g].sum()
               for g in np.unique(grp) if (grp == g).sum() >= 3)


def find_islands_combined(peaks, wavelength, candidate_floor=CANDIDATE_FLOOR,
                          gap_factor=GAP_FACTOR):
    """One grouping, two measures: continuous pre-risk and incumbent hard."""
    cand = (peaks[peaks["amplitude"] >= candidate_floor]
            .sort_values("Location_m").reset_index(drop=True))
    if cand.empty:
        return pd.DataFrame()
    group = (cand["Location_m"].diff() > gap_factor * wavelength).cumsum()
    out = []
    for _, g in cand.groupby(group):
        locs, amps = g["Location_m"].to_numpy(), g["amplitude"].to_numpy()
        out.append({
            "center_location": locs.mean(),
            "start_location": locs[0], "end_location": locs[-1],
            "amplitude": UP_MULTIPLIER * float((amps * soft_weight(amps)).sum()),  # continuous
            "hard_amplitude": _hard_amplitude(locs, amps, wavelength, gap_factor),  # incumbent
        })
    return pd.DataFrame(out)


def build_all_combined(peaks, wavelength, **kw):
    out = []
    for (elr, track, date), g in peaks.groupby(["ELR", "TrackID", "date"]):
        isl = find_islands_combined(g, wavelength, **kw)
        if not isl.empty:
            isl["ELR"], isl["TrackID"], isl["date"] = elr, track, date
            out.append(isl)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()
