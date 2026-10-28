"""experiments/exp04_multiband_watchlist.py
Multi-band cyclic-top watchlist. exp01-03 screened 9m only; exp04 showed ~a third
of critical locations are long-wavelength (13.5/18m) defects invisible to 9m.
This runner screens 9m, 13.5m and 18m, scores each band with the exp02
severity-memory model (fit per band), and reconciles overlapping footprints into
one per-location watchlist (worst band governs). 4.5/6m excluded (negligible on
the hard scale, exp04 stage 1). Scores are fit-on-all for operational ranking;
honest LOO generalisation of the severity-memory model was established in exp02.

    python -m experiments.exp04_multiband_watchlist
"""
import json
import pandas as pd
import config
from cprics.io_data import load_peak_amplitudes
from cprics.continuous import build_all_combined, CANDIDATE_FLOOR
from cprics.tracking import track_islands
from cprics import escalation as esc
from cprics.reconcile import reconcile_locations
from cprics.location import to_mileage

NAME = "exp04_multiband_watchlist"
BANDS = {"9": ("9_top_right", 9.0, "9R"),
         "13.5": ("135_top_right", 13.5, "135R"),
         "18": ("18_top_right", 18.0, "18R")}
CONCERN, CRITICAL = 18.0, 30.0


def band_table(chan, wl, tag):
    isl = track_islands(build_all_combined(load_peak_amplitudes(config.PEAK_AMP_DIR, chan),
                                           wavelength=wl, candidate_floor=CANDIDATE_FLOOR), tag=tag)
    t = (isl.groupby(["site_id", "date"])
            .agg(amp=("amplitude", "max"), hard=("hard_amplitude", "max"))
            .reset_index().sort_values("date"))
    s = t.groupby("site_id").agg(current_amp=("amp", "last"), max_amp=("amp", "max"),
                                 max_hard=("hard", "max"))
    s = s.join(isl.groupby("site_id").agg(ELR=("ELR", "first"), TrackID=("TrackID", "first"),
                                          start=("start_location", "min"), end=("end_location", "max")))
    s["critical"] = s.max_hard >= CRITICAL
    model = esc.fit_escalation(s.reset_index(), s.critical.astype(int).values, ["current_amp", "max_amp"])
    esc.save_escalation(model, config.MODELS_DIR / f"{NAME}_{tag}_model.json")
    s["score"] = pd.Series(esc.escalation_scores(s.reset_index(), model)).reindex(s.index).round(3)
    return s


def main():
    exp_dir = config.OUTPUTS_DIR / NAME
    (exp_dir / "tables").mkdir(parents=True, exist_ok=True)

    flagged = []
    for name, (chan, wl, tag) in BANDS.items():
        print(f"[{NAME}] band {name}m ...")
        s = band_table(chan, wl, tag)
        f = s[s.max_hard >= CONCERN].reset_index(); f["band"] = name + "m"
        flagged.append(f[["band", "ELR", "TrackID", "start", "end", "max_hard", "score"]])
    flagged = pd.concat(flagged, ignore_index=True)

    locs = reconcile_locations(flagged, critical_mm=CRITICAL)
    locs["has_9m"] = locs.bands.apply(lambda b: "9m" in b.split("+"))
    locs["location"] = [f"{to_mileage(a)}-{to_mileage(b)}" for a, b in zip(locs.start, locs.end)]
    locs = locs.sort_values(["critical", "score"], ascending=[False, False])

    locs[["ELR", "TrackID", "location", "bands", "worst_hard", "score", "critical"]] \
        .to_excel(exp_dir / "tables" / "watchlist.xlsx", index=False)

    crit = locs[locs.critical]
    findings = {
        "experiment": NAME, "bands": list(BANDS), "concern_mm": CONCERN, "critical_mm": CRITICAL,
        "watchlist_locations": int(len(locs)),
        "critical_locations": int(len(crit)),
        "nine_only_watchlist": int(locs.has_9m.sum()),
        "critical_covered_by_9m_only": int(crit.has_9m.sum()),
        "critical_missed_by_9m_only": int((~crit.has_9m).sum()),
    }
    with open(exp_dir / "findings.json", "w") as fh:
        json.dump(findings, fh, indent=2)
    print(f"Wrote {len(locs)} locations -> {exp_dir / 'tables' / 'watchlist.xlsx'}")
    print(json.dumps(findings, indent=2))


if __name__ == "__main__":
    main()
