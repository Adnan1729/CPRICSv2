# exp01_continuous_9R
**Technique:** wavelength-aware islands + sigmoid-continuous severity, 9 m right rail; sites ranked by risk score.
**Status:** baseline (git tag `v1-baseline`) · **Date:** 2026-10-26

## Files
- Config: `experiments/exp01_continuous_9R.py`
- Reproduce: `python run_pipeline.py exp01_continuous_9R`
- Watchlist: `outputs/exp01_continuous_9R/tables/watchlist.xlsx`
- Figures: `outputs/exp01_continuous_9R/figures/*.html`
- Metrics: `outputs/exp01_continuous_9R/metrics.json`
- Frozen archetypes: `models/exp01_continuous_9R_archetypes.json`

## Technique
Consumes Network Rail's standard peak-amplitude output. Islands = runs of peaks
within 1.5 wavelengths; severity accumulated with a sigmoid weight (removes the
hard 5 mm cliff); islands tracked across dates; sites classified into four
archetypes; ranked by a transparent risk score (severity + growth).

## Results (scorecard)
Population: 2263 sites, 22 critical (base rate 0.97%).
- **Ranking:** AUPRC 0.589 (vs 0.01 base). Top 20 by risk: 65% critical, holds 59% of all criticals. Top 50: 34% critical, holds 77%.
- **Screening:** watchlist 91; precision 24%; recall 100%; 4.14 flags per critical.
- **Advance warning:** 55% of criticals warned early (12/22); median lead 12.0 months; 9/22 caught with ≥3 months usable lead.
- **vs Module 11:** C-PRICS 55% advance / 12.0 mo  vs  Module 11 45% / 10.1 mo.
- **False positives (69):** 34 Saw-tooth (tamped saves), 34 Steady climber (rising), 1 Severe.

## Limitations
- Single channel (9 m, right rail).
- No advance warning on ~45% of critical sites (sudden onset — needs other bands / TG geometry).
- No exact failure-date forecasting.
- Location→mileage origin not yet cross-checked vs CYC.
