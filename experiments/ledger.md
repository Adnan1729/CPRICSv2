# C-PRICS experiment ledger

Scored on the C-PRICS scorecard (`cprics/metrics.py`). Critical base rate = 0.97%
(so AUPRC is vs ~0.01). Adv% = criticals warned before going critical; Lead =
median advance warning (months); M11 = Module 11 on the identical basis.

| Exp | Technique | Channel | AUPRC | P@20 | Recall | Flags/crit | Adv% | Lead | M11 Adv% | M11 Lead | Record |
|-----|-----------|---------|-------|------|--------|------------|------|------|----------|----------|--------|
| exp01_continuous_9R | Islands + sigmoid-continuous severity, ranked by risk score | 9 m / R | 0.589 | 0.65 | 1.00 | 4.14 | 55% | 12.0 | 45% | 10.1 | [record](exp01_continuous_9R.md) |
| exp02_supervised_9R | supervised escalation ranking (logistic: current_amp + max_amp), LOO | 0.853 | 0.75 | 0.44 | R@50 1.0 — top 50 of 91 catches all 22 critical (exp01 0.77); severity memory recovers 6 tamped chronic sites (median peak 43.7mm); growth/shape add nothing; 7-feat overfits (0.78). Model: models/exp02_supervised_9R_model.json |
| exp03_multiband_9R | cross-band (multi-wavelength) texture: coverage + ranking + equal-budget early warning | 0.854 | — | — | NEGATIVE (no lift vs base 0.853). At equal 176-site budget multiband is WORSE than 9m: capture 18/22 vs 22/22, advance 27.3% vs 54.5%, rescued 1/10 sudden. Bands are Butterworth-filtered from the same Top35 -> correlated with 9m, no independent signal. Not disproven for ride-quality (no label). Notebook: notebooks/research/10_exp03_multiband.ipynb |
| exp04_multiband_watchlist | multi-band watchlist: screen 9/13.5/18m, severity-memory per band, reconcile by footprint overlap | — | — | — | POSITIVE. 9m-only misses 12/36 critical locations (long-wavelength 13.5/18m defects); multi-band catches 36/36. Watchlist 57->100 locations (+75%). Runner: experiments/exp04_multiband_watchlist.py; models/exp04_multiband_watchlist_*_model.json; outputs/exp04_multiband_watchlist/ |

