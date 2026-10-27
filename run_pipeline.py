"""run_pipeline.py — run one named C-PRICS experiment end to end.
    python run_pipeline.py exp01_continuous_9R
Writes outputs/<experiment>/ (watchlist.xlsx + metrics.json). Does NOT re-cluster.
"""
import sys, json, importlib
import pandas as pd
import config
from cprics.io_data import load_peak_amplitudes
from cprics.continuous import build_all_combined
from cprics.tracking import track_islands
from cprics.features import build_feature_table
from cprics.classify import assign_archetype
from cprics.risk import risk_score
from cprics.location import to_mileage
from cprics.metrics import site_eval_table, scorecard

PRIORITY = {"Severe": "1 - act now", "Steady climber": "2 - proactive watch",
            "Saw-tooth": "3 - review renewal", "Dormant": "4 - monitor"}


def main(exp_name):
    exp = importlib.import_module(f"experiments.{exp_name}")
    P = exp.PARAMS
    exp_dir = config.OUTPUTS_DIR / exp.NAME
    (exp_dir / "tables").mkdir(parents=True, exist_ok=True)

    print(f"[{exp.NAME}] loading peak amplitudes ...")
    pk = load_peak_amplitudes(config.PEAK_AMP_DIR, P["channel"])
    print(f"[{exp.NAME}] building and tracking islands ...")
    isl = track_islands(
        build_all_combined(pk, wavelength=P["wavelength"], candidate_floor=P["candidate_floor"]),
        max_center_gap=P["tracking_gap_m"])

    print(f"[{exp.NAME}] assigning archetypes ...")
    feats = build_feature_table(isl, min_obs=3).merge(
        isl.groupby("site_id")["amplitude"].max().rename("cont_max"), on="site_id")
    with open(config.MODELS_DIR / f"{exp.NAME}_archetypes.json") as fh:
        feats["archetype"] = assign_archetype(feats, json.load(fh))
    arch = dict(zip(feats.site_id, feats.archetype))

    print(f"[{exp.NAME}] building watchlist ...")
    rows, score_by_site = [], {}
    for sid, g in isl.groupby("site_id"):
        if sid not in arch:
            continue
        g = g.sort_values("date"); last = g.iloc[-1]
        t = g.groupby("date", as_index=False)["amplitude"].max().sort_values("date")
        r = round(risk_score(t), 3)
        score_by_site[sid] = r                      # the ranking score for exp01
        rows.append({"archetype": arch[sid], "priority": PRIORITY[arch[sid]],
                     "ELR": last["ELR"], "TrackID": int(last["TrackID"]),
                     "location": f"{to_mileage(last['start_location'])}-{to_mileage(last['end_location'])}",
                     "current_amp_mm": round(t["amplitude"].iloc[-1], 1), "risk": r,
                     "last_inspection": pd.to_datetime(last["date"]).date(), "site_id": sid})
    watch = pd.DataFrame(rows).sort_values(["priority", "current_amp_mm"], ascending=[True, False])
    watch.to_excel(exp_dir / "tables" / "watchlist.xlsx", index=False)
    print(f"Wrote {len(watch)} sites -> {exp_dir / 'tables' / 'watchlist.xlsx'}")

    print(f"[{exp.NAME}] scoring ...")
    T = site_eval_table(isl, score_by_site, arch, P["concern_mm"], P["critical_mm"])
    metrics = scorecard(T)
    with open(exp_dir / "metrics.json", "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(json.dumps(metrics, indent=2, default=str))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "exp01_continuous_9R")
