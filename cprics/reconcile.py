"""cprics/reconcile.py — merge per-band flagged sites into one per-location watchlist.

Two cyclic tops at the same ELR/TrackID whose island footprints overlap are the
same physical location, whichever wavelength band flagged them. The overlap test
needs no tolerance parameter: exp04 showed the result is flat from 0 to 20 m,
because real merges happen on footprint overlap, not on an arbitrary gap.
"""
import pandas as pd


def reconcile_locations(flagged, critical_mm=30.0):
    """flagged: one row per flagged band-site, columns
         band, ELR, TrackID, start, end, max_hard, score.
       Returns one row per physical location with the bands that flagged it,
       its worst hard amplitude, and its ranking score (worst across bands)."""
    f = flagged.copy()
    f["center"] = (f["start"] + f["end"]) / 2
    f = f.sort_values(["ELR", "TrackID", "center"]).reset_index(drop=True)
    loc, k, pe, pELR, pTID = [], 0, None, None, None
    for _, r in f.iterrows():
        if pe is not None and r.ELR == pELR and r.TrackID == pTID and (r.start - pe) <= 0:
            loc.append(k); pe = max(pe, r.end)
        else:
            k += 1; loc.append(k); pe, pELR, pTID = r.end, r.ELR, r.TrackID
    f["loc"] = loc
    out = f.groupby("loc").agg(
        ELR=("ELR", "first"), TrackID=("TrackID", "first"),
        start=("start", "min"), end=("end", "max"),
        bands=("band", lambda s: "+".join(sorted(set(s), key=lambda b: float(str(b).rstrip("m"))))),
        worst_hard=("max_hard", "max"), score=("score", "max"))
    out["critical"] = out["worst_hard"] >= critical_mm
    return out.reset_index(drop=True)
