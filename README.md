# C-PRICS v2 — Continuous Pre-Risk Intelligent Category Space

Proactive cyclic-top risk for railway track geometry. Builds on Network Rail's
standard cyclic-top signal processing and adds continuous pre-risk scoring,
island tracking over time, and fault-type classification.

## What it does
Peak-amplitude data (per ELR / TrackID / date) in → a ranked watchlist of
cyclic-top sites out, each with its location (mileage), current severity,
fault archetype, and priority.

## Run
    python run_pipeline.py

Reads paths and parameters from `config.py`, writes `outputs/tables/watchlist_9R.xlsx`.
Uses the frozen archetypes in `models/`; it does **not** re-cluster — archetype
discovery is a deliberate offline step.

## Layout
- `cprics/` — the library (all logic)
- `run_pipeline.py` — production entry point
- `models/` — frozen fault archetypes
- `notebooks/research/` — how it was built and validated
- `notebooks/reports/` — generates the shareable figures and tables
- `tests/` — unit tests
- `config.py` — paths and parameters

## Inputs (git-ignored)
- `data/Data_Out_Peak_Amp/` — Network Rail peak-amplitude output
- `data/CYC/` — incumbent exceedance reports (baseline / validation)

## Install
    python -m venv .venv && source .venv/Scripts/activate
    pip install -r requirements.txt
