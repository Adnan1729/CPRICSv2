# exp04_multiband_watchlist — POSITIVE (scope correction)

**Question:** is 9m the right single band to screen, or do serious cyclic tops
live at other wavelengths a 9m-only watchlist never sees?

**Design:** screen 9m, 13.5m, 18m independently (exp02 severity-memory model per
band, fit-on-all for ranking), flag at concern (hard>=18), reconcile overlapping
island footprints into one per-location watchlist (worst band governs). 4.5/6m
excluded — negligible on the hard scale.

## Findings
Per-band severity sweep (max hard amplitude per site):

| band  | critical >=30 | concern >=18 | p99  | max  |
|-------|---------------|--------------|------|------|
| 4.5m  | 0             | 1            | 0.0  | 18.6 |
| 6m    | 1             | 5            | 0.0  | 40.6 |
| 9m    | 31            | 99           | 30.3 | 80.7 |
| 13.5m | 11            | 53           | 23.9 | 64.5 |
| 18m   | 23            | 76           | 29.7 | 71.3 |

Cross-band overlap (footprint overlap; GAP-insensitive, flat 0-20m):
- 36 distinct critical locations; 9m and long bands almost never overlap (3/36).
- 9m-only covers 24/36 and misses **12 entirely** (long-wavelength defects with
  no 9m concern signal).

Reconciled multi-band watchlist:
- critical coverage 24/36 -> **36/36**.
- watchlist 57 -> 100 locations (+43, +75%); of the 43, 12 are new criticals,
  31 are long-band concern-level sites.

## Verdict
The serious problem is MULTI-BAND in COVERAGE — 9m/13.5m/18m host largely
distinct critical populations, so a 9m-only C-PRICS misses a third of critical
locations. Multi-band screening is the correct production design. (Contrast
exp03: multi-band does NOT help TEXTURE/ranking — different question.)

## Cost / open decision
Full coverage costs a +75% larger watchlist. For a safety list that is a
worthwhile trade; per-band concern thresholds could trim the non-critical
additions, pending the threshold question below.

## Open question for Andy / Module 11
exp04 used universal 18/30mm thresholds. Empirically 9/13.5/18m sit on a similar
hard scale (p99 ~24-30), so roughly fair — but confirm whether the M11 category
thresholds are per-wavelength or universal.

## Reproduce
`python -m experiments.exp04_multiband_watchlist`
Runner: experiments/exp04_multiband_watchlist.py · Reconcile: cprics/reconcile.py
Band-aware IDs: track_islands(tag=...) · Models: models/exp04_multiband_watchlist_{9R,135R,18R}_model.json
Outputs: outputs/exp04_multiband_watchlist/ · Diagnostic: notebooks/research/11_exp04_bandsweep.ipynb
