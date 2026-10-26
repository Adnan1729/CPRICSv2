
# exp01_continuous_9R

**Technique:** wavelength-aware islands + sigmoid-continuous severity, 9 m right rail.
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
archetypes; ranked watchlist produced.

## Results

- Validation vs Module 11: amplitude 22.0 vs 21.7 mm (reproduces the standard).
- Screening: 2263 sites, 22 critical (1.0%); watchlist 91; precision 24%, recall 100%, ~24x lift.
- Advance warning: 12/22 (55%) critical sites warned early; median lead 12 months (IQR 3.4-14.9).
- Archetypes: Dormant 2172, Saw-tooth 45, Steady climber 44, Severe 2.
- False positives (69): 34 Saw-tooth (tamped saves), 34 Steady climber (rising), 1 Severe.

## Limitations

- Single channel (9 m, right rail).
- No advance warning on ~45% of critical sites (sudden onset).
- No exact failure-date forecasting.
- Location->mileage origin not yet cross-checked vs CYC.
