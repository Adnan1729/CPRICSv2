# C-PRICS experiment ledger

Scored on the C-PRICS scorecard (`cprics/metrics.py`). Critical base rate = 0.97%
(so AUPRC is vs ~0.01). Adv% = criticals warned before going critical; Lead =
median advance warning (months); M11 = Module 11 on the identical basis.

| Exp | Technique | Channel | AUPRC | P@20 | Recall | Flags/crit | Adv% | Lead | M11 Adv% | M11 Lead | Record |
|-----|-----------|---------|-------|------|--------|------------|------|------|----------|----------|--------|
| exp01_continuous_9R | Islands + sigmoid-continuous severity, ranked by risk score | 9 m / R | 0.589 | 0.65 | 1.00 | 4.14 | 55% | 12.0 | 45% | 10.1 | [record](exp01_continuous_9R.md) |
| exp02_supervised_9R | supervised escalation ranking (logistic: current_amp + max_amp), LOO | 0.853 | 0.75 | 0.44 | R@50 1.0 — top 50 of 91 catches all 22 critical (exp01 0.77); severity memory recovers 6 tamped chronic sites (median peak 43.7mm); growth/shape add nothing; 7-feat overfits (0.78). Model: models/exp02_supervised_9R_model.json |
