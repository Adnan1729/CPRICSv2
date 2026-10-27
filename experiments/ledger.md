# C-PRICS experiment ledger

Scored on the C-PRICS scorecard (`cprics/metrics.py`). Critical base rate = 0.97%
(so AUPRC is vs ~0.01). Adv% = criticals warned before going critical; Lead =
median advance warning (months); M11 = Module 11 on the identical basis.

| Exp | Technique | Channel | AUPRC | P@20 | Recall | Flags/crit | Adv% | Lead | M11 Adv% | M11 Lead | Record |
|-----|-----------|---------|-------|------|--------|------------|------|------|----------|----------|--------|
| exp01_continuous_9R | Islands + sigmoid-continuous severity, ranked by risk score | 9 m / R | 0.589 | 0.65 | 1.00 | 4.14 | 55% | 12.0 | 45% | 10.1 | [record](exp01_continuous_9R.md) |
