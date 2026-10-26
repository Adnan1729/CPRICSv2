"""cprics/islands.py — group consecutive cyclic-top peaks into islands.

An island is a run of >=3 peaks (each >= the amplitude threshold) where
consecutive peaks sit within ~1.5 wavelengths of each other: a genuine
repeating pattern at that wavelength. Its severity is the incumbent's
accumulated measure: 0.8 x the sum of its peak amplitudes.
"""
import pandas as pd

AMP_THRESHOLD = 5.0      # mm; a peak must reach this to count (NR standard)
GAP_FACTOR    = 1.5      # consecutive peaks within gap_factor * wavelength
MIN_PEAKS     = 3        # a cyclic top needs at least 3 peaks
UP_MULTIPLIER = 0.8      # NR accumulation multiplier


def find_islands(peaks, wavelength, amp_threshold=AMP_THRESHOLD,
                 gap_factor=GAP_FACTOR, min_peaks=MIN_PEAKS,
                 up_multiplier=UP_MULTIPLIER):
    """Group one date's peaks (one section, one channel) into islands."""
    strong = (peaks[peaks["amplitude"] >= amp_threshold]
              .sort_values("Location_m").reset_index(drop=True))
    if len(strong) < min_peaks:
        return pd.DataFrame()

    max_gap = gap_factor * wavelength
    group = (strong["Location_m"].diff() > max_gap).cumsum()   # new island on a big gap

    islands = []
    for _, g in strong.groupby(group):
        if len(g) < min_peaks:
            continue
        islands.append({
            "start_location": g["Location_m"].iloc[0],
            "end_location": g["Location_m"].iloc[-1],
            "center_location": g["Location_m"].mean(),
            "n_peaks": len(g),
            "max_peak": g["amplitude"].max(),
            "amplitude": up_multiplier * g["amplitude"].sum(),   # incumbent measure
        })
    return pd.DataFrame(islands)


def build_all_islands(peaks, wavelength, **kw):
    """Islands for every section and date."""
    out = []
    for (elr, track, date), g in peaks.groupby(["ELR", "TrackID", "date"]):
        isl = find_islands(g, wavelength, **kw)
        if not isl.empty:
            isl["ELR"], isl["TrackID"], isl["date"] = elr, track, date
            out.append(isl)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()
