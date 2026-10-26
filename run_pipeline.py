"""run_pipeline.py — C-PRICS production entry point.

Peak-amplitude data in -> ranked cyclic-top watchlist out (Excel).
    python run_pipeline.py
Paths/parameters come from config.py. Uses the frozen archetypes in models/;
it does NOT re-cluster (discovery is done offline, deliberately).
"""
import json
import pandas as pd
import config
from cprics.io_data import load_peak_amplitudes
from cprics.continuous import build_all_combined
from cprics.tracking import track_islands
from cprics.features import build_feature_table
from cprics.classify import assign_archetype
from cprics.risk import risk_score
from cprics.location import to_mileage

CHANNEL, WAVELENGTH = "9_top_right", 9
PRIORITY = {"Severe": "1 - act now", "Steady climber": "2 - proactive watch",
            "Saw-tooth": "3 - review renewal", "Dormant": "4 - monitor"}


def main():
    print("Loading peak amplitudes ...")
    pk = load_peak_amplitudes(config.PEAK_AMP_DIR, CHANNEL)

    print("Building and tracking islands ...")
    isl = track_islands(build_all_combined(pk, wavelength=WAVELENGTH))

    print("Scoring sites ...")
    feats = build_feature_table(isl, min_obs=3)
    feats = feats.merge(isl.groupby("site_id")["amplitude"].max().rename("cont_max"),
                        on="site_id")
    with open(config.MODELS_DIR / "archetypes_9R.json") as fh:
        frozen = json.load(fh)
    feats["archetype"] = assign_archetype(feats, frozen)
    arch = dict(zip(feats.site_id, feats.archetype))

    rows = []
    for sid, g in isl.groupby("site_id"):
        if sid not in arch:                      # only sites with >=3 inspections
            continue
        g = g.sort_values("date")
        last = g.iloc[-1]
        t = (g.groupby("date", as_index=False)["amplitude"].max().sort_values("date"))
        rows.append({
            "archetype": arch[sid],
            "priority": PRIORITY[arch[sid]],
            "ELR": last["ELR"], "TrackID": int(last["TrackID"]),
            "location": f"{to_mileage(last['start_location'])}-{to_mileage(last['end_location'])}",
            "current_amp_mm": round(t["amplitude"].iloc[-1], 1),
            "risk": round(risk_score(t), 2),
            "last_inspection": pd.to_datetime(last["date"]).date(),
            "site_id": sid,
        })
    watch = (pd.DataFrame(rows)
             .sort_values(["priority", "current_amp_mm"], ascending=[True, False]))

    out = config.OUTPUTS_DIR / "tables" / "watchlist_9R.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    watch.to_excel(out, index=False)
    print(f"\nWrote {len(watch)} sites -> {out}")
    print(watch["archetype"].value_counts().to_string())


if __name__ == "__main__":
    main()
