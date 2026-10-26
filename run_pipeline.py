"""run_pipeline.py — run one named C-PRICS experiment end to end.

    python run_pipeline.py exp01_continuous_9R

Peak-amplitude data in -> ranked watchlist (Excel) + metrics.json out, all
under outputs/<experiment>/. Reads that experiment's frozen archetypes from
models/<experiment>_archetypes.json. Does NOT re-cluster.
"""
import sys
import json
import importlib
import pandas as pd
import config
from cprics.io_data import load_peak_amplitudes
from cprics.continuous import build_all_combined
from cprics.tracking import track_islands
from cprics.features import build_feature_table
from cprics.classify import assign_archetype
from cprics.risk import risk_score
from cprics.location import to_mileage
from cprics.evaluate import compute_metrics

PRIORITY = {"Severe": "1 - act now", "Steady climber": "2 - proactive watch",
            "Saw-tooth": "3 - review renewal", "Dormant": "4 - monitor"}


def main(exp_name):
    # load this experiment's config (its parameters live in experiments/<exp_name>.py)
    exp = importlib.import_module(f"experiments.{exp_name}")
    P = exp.PARAMS

    exp_dir = config.OUTPUTS_DIR / exp.NAME
    (exp_dir / "tables").mkdir(parents=True, exist_ok=True)

    print(f"[{exp.NAME}] loading peak amplitudes ...")
    pk = load_peak_amplitudes(config.PEAK_AMP_DIR, P["channel"])

    print(f"[{exp.NAME}] building and tracking islands ...")
    isl = track_islands(
        build_all_combined(pk, wavelength=P["wavelength"],
                           candidate_floor=P["candidate_floor"]),
        max_center_gap=P["tracking_gap_m"])

    print(f"[{exp.NAME}] assigning archetypes ...")
    feats = build_feature_table(isl, min_obs=3).merge(
        isl.groupby("site_id")["amplitude"].max().rename("cont_max"), on="site_id")
    with open(config.MODELS_DIR / f"{exp.NAME}_archetypes.json") as fh:
        frozen = json.load(fh)
    feats["archetype"] = assign_archetype(feats, frozen)
    arch = dict(zip(feats.site_id, feats.archetype))

    print(f"[{exp.NAME}] building watchlist ...")
    rows = []
    for sid, g in isl.groupby("site_id"):
        if sid not in arch:                      # only sites with >=3 inspections
            continue
        g = g.sort_values("date")
        last = g.iloc[-1]
        t = g.groupby("date", as_index=False)["amplitude"].max().sort_values("date")
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

    watch.to_excel(exp_dir / "tables" / "watchlist.xlsx", index=False)
    print(f"Wrote {len(watch)} sites -> {exp_dir / 'tables' / 'watchlist.xlsx'}")

    # headline numbers, saved next to the watchlist
    metrics = compute_metrics(isl, arch, P["concern_mm"], P["critical_mm"])
    with open(exp_dir / "metrics.json", "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print("metrics:", metrics)


if __name__ == "__main__":
    exp_name = sys.argv[1] if len(sys.argv) > 1 else "exp01_continuous_9R"
    main(exp_name)
