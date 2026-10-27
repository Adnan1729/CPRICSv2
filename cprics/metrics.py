"""cprics/metrics.py — the C-PRICS scorecard.

One definition of how every experiment is scored, so experiments compare on the
same footing. Chosen for a rare-event, ranked, time-sensitive rail problem —
not accuracy/F1, which mislead here.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score


def site_eval_table(isl, score_by_site, archetype_by_site, concern=18, critical=30):
    """One row per site: outcome, C-PRICS and Module 11 flag timing, rank score, archetype.

    score_by_site: dict site_id -> value used to RANK (risk score for exp01,
                   escalation probability for exp02). Higher = worse.
    """
    def lead(flag_dates, crit_date, is_crit):
        if not is_crit:
            return np.nan
        d = flag_dates[flag_dates < crit_date]
        return (crit_date - d.min()).days / 30.44 if len(d) else np.nan

    rows = []
    for sid, g in isl.groupby("site_id"):
        if sid not in score_by_site:
            continue
        g = g.sort_values("date")
        is_crit = g["hard_amplitude"].max() >= critical
        cd = g.loc[g["hard_amplitude"] >= critical, "date"].min() if is_crit else pd.NaT
        cpr = g.loc[g["amplitude"] >= concern, "date"]            # C-PRICS flag
        m11 = g.loc[g["hard_amplitude"] >= concern, "date"]       # Module 11 flag
        rows.append({
            "site_id": sid, "score": score_by_site[sid],
            "archetype": archetype_by_site.get(sid), "critical": bool(is_crit),
            "cprics_flagged": len(cpr) > 0, "cprics_lead": lead(cpr, cd, is_crit),
            "m11_flagged": len(m11) > 0, "m11_lead": lead(m11, cd, is_crit),
        })
    return pd.DataFrame(rows)


def scorecard(T, ks=(20, 50), actionable_months=3):
    """Full C-PRICS scorecard from a site-eval table."""
    n = len(T); nc = int(T["critical"].sum())
    flag, crit = T["cprics_flagged"], T["critical"]
    TP = int((flag & crit).sum()); FP = int((flag & ~crit).sum()); FN = int((~flag & crit).sum())

    R = T.sort_values("score", ascending=False)
    p_at_k = {k: round(float(R.head(k)["critical"].mean()), 3) for k in ks}
    r_at_k = {k: round(float(R.head(k)["critical"].sum()) / nc, 3) if nc else None for k in ks}
    auprc = float(average_precision_score(crit.astype(int), T["score"])) if nc else None

    adv = T[crit & T["cprics_lead"].notna()]
    m11_adv = T[crit & T["m11_lead"].notna()]
    fp = T[flag & ~crit]

    return {
        "n_sites": n, "n_critical": nc, "base_rate": round(nc / n, 4),
        # screening
        "watchlist_size": TP + FP,
        "flags_per_critical": round((TP + FP) / nc, 2) if nc else None,
        "precision": round(TP / (TP + FP), 3) if TP + FP else None,
        "recall": round(TP / (TP + FN), 3) if TP + FN else None,
        # ranking (operational)
        "auprc": round(auprc, 3) if auprc is not None else None,
        "precision_at_k": p_at_k, "recall_at_k": r_at_k,
        # timeliness
        "advance_pct": round(len(adv) / nc, 3) if nc else None,
        "median_lead_months": round(float(adv["cprics_lead"].median()), 1) if len(adv) else None,
        f"caught_ge_{actionable_months}mo": int((adv["cprics_lead"] >= actionable_months).sum()),
        # head-to-head vs Module 11
        "m11_advance_pct": round(len(m11_adv) / nc, 3) if nc else None,
        "m11_median_lead_months": round(float(m11_adv["m11_lead"].median()), 1) if len(m11_adv) else None,
        # false-positive composition
        "fp_total": int(len(fp)), "fp_by_archetype": fp["archetype"].value_counts().to_dict(),
    }
