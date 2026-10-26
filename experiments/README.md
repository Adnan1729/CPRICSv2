# Experiments

Every attempt is a named experiment `expNN_<technique>`. Nothing is ever
overwritten — a new idea is a new experiment.

## Each experiment owns these, by name

- `experiments/expNN_<technique>.py`  — its config (never edited after running)
- `experiments/expNN_<technique>.md`  — its record: technique, results, file paths
- `outputs/expNN_<technique>/`         — its figures/, tables/, metrics.json
- `models/expNN_<technique>_*.json`    — its frozen models
- a row in `ledger.md`                 — the one-line comparison + link to its record

## Rules

- New algorithm → a new function in `cprics/` (don't edit the old one); the config selects it.
- Run with:  `python run_pipeline.py expNN_<technique>`  → writes everything under its own name.
- `metrics.json` is written automatically, so results are always attributable and located.

## Scaling across wavelengths

Each band/rail is its own experiment (`exp02_continuous_18R`, `exp03_continuous_13R`, …),
validated against the incumbent per band. The unified per-location watchlist that combines
all bands/rails (worst-of reconciliation) is its own experiment (`exp10_unified`).
