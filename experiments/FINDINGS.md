# C-PRICS — Experimental Findings (technical briefing)

A review of experiments exp01–exp04. Audience: signal-processing / track-
geometry. C-PRICS adds an analysis and prioritisation layer; it does not alter
the signal processing.

## 1. What C-PRICS is, and is not
- It consumes the Butterworth band outputs (peak amplitudes per wavelength) and
  never touches anything upstream. The entire boundary is one function:
  cprics/io_data.py:load_peak_amplitudes, which reads `amplitude` unchanged.
- There are no risk labels. We use an OPERATIONAL definition: a site is
  "critical" if its accumulated hard amplitude ever reaches 30mm (the top
  Module 11 category, "I"), "concern" at 18mm (entry category "D"). This is a
  proxy for actionability, not a confirmed safety outcome — stated plainly.
- Goal: turn the per-wavelength 5mm peak picture into a ranked, history-aware,
  multi-band watchlist.

## 2. Method, in brief (file map)
- **Islands** (cprics/islands.py, continuous.py): a cyclic top is a run of peaks
  within 1.5x wavelength; the 1.5x sits in the valley of the peak-gap histogram
  (peaks cluster at ~1 wavelength, gap after ~12m).
- **Continuous measure — the "C"** (continuous.py:soft_weight): each peak is
  weighted by a sigmoid centred at 5mm, removing the hard 5mm cliff. The
  incumbent hard count is computed alongside (hard_amplitude) for comparison.
- **Tracking** (cprics/tracking.py): islands are linked across inspections by
  footprint proximity into "sites"; gradual drift is followed by chaining.
- **Severity-memory model** (cprics/escalation.py): logistic on two features —
  current amplitude and worst-ever amplitude.
- **Metrics** (cprics/metrics.py): AUPRC, precision/recall@K, advance-warning %,
  lead time — deliberately NOT accuracy/F1 (1% base rate makes them misleading).
- **Reconciliation** (cprics/reconcile.py): overlapping island footprints across
  bands are merged into one physical location.

## 3. The four experiments

| exp | question | result |
|-----|----------|--------|
| 01 | baseline: continuous + hand-weighted risk | AUPRC 0.589, R@50 0.77 |
| 02 | rank on severity *memory* | AUPRC 0.853, R@50 1.0 — **win** |
| 03 | does cross-band *texture* (jaggedness) help? | **negative** |
| 04 | is 9m the right band to *screen* on? | **no — multi-band needed** |

### exp01 — baseline
Ranked by 0.6*severity + 0.4*growth. AUPRC 0.589, P@20 0.65, R@50 0.77, advance
54.5%. Works, but sees only current state, so it blind-spots sites that spiked
and were tamped.

### exp02 — severity memory (the main win)
Rank by current AND worst-ever amplitude (2-feature logistic). AUPRC
0.589 -> 0.853, P@20 0.65 -> 0.75, R@50 0.77 -> 1.0 (all 22 critical sites in the
top 50). Mechanism: 6 of 22 critical sites currently sit below 24mm but peaked at
a median 43.7mm before tamping — chronic repeat offenders a current-state score
misses. Negatives banked: trajectory shape and growth-rate add nothing
(behaviour-only AUPRC 0.586 ~= baseline); larger feature sets overfit at 22
positives (7-feature 0.78 < 2-feature 0.85). The signal is severity, full stop.

### exp03 — multi-band texture (NEGATIVE)
Tested the "jaggier = riskier/earlier" intuition via short-wavelength energy
co-located with the 9m top. Critical sites are broadband (100% carry 6/13.5m
energy) — but that tracks feature SIZE, not escalation. Texture added nothing to
ranking (0.853 -> 0.854), and at an equal 176-site budget a multi-band early-
warning flag was WORSE than 9m alone (capture 18/22 vs 22/22, advance 27% vs
55%). The apparent "45% -> 68% advance" was purely a 3x-watchlist artifact.
Reason: all bands are Butterworth-filtered from the same Top35 signal, so they
are correlated with 9m and carry little independent signal for escalation.
Caveat: tested against amplitude-escalation, not ride quality — not disproven for
ride quality, which we have no label for.

### exp04 — multi-band coverage (POSITIVE, scope correction)
A different question from exp03. Per-band sweep: critical populations exist at 9m
(31), 18m (23) and 13.5m (11); 4.5/6m are negligible. The three main bands sit on
a similar severity scale (p99 ~24-30). Overlap analysis: 36 distinct critical
locations, of which 9m and the long bands almost never coincide (3/36). A 9m-only
watchlist misses **12 critical locations entirely** — long-wavelength defects.
The reconciled multi-band watchlist (9/13.5/18m) catches all 36, at a cost of
57 -> 100 watchlist locations (+75%).

## 4. Cross-cutting observations
- **Severity is the dominant predictor.** Current + worst-ever amplitude carries
  essentially all the escalation signal; behaviour, growth-rate and jaggedness
  add nothing (exp02, exp03).
- **"Multi-band" means two different things.** It does NOT improve single-band
  *prediction* (texture, exp03) but it is essential for *coverage* (exp04): the
  serious defects are spread across wavelengths as distinct populations.
- **Nothing is a black box.** Every step is an inspectable rule or a 2-feature
  logistic whose coefficients we can show. No deep learning, by choice.

## 5. Reproducibility
Every experiment has a ledger row (experiments/ledger.md), a record .md, and an
outputs/<name>/ folder. Pipeline experiments (01, 02, 04) have configs/runners
and frozen models; research/negative experiments (03) live in notebooks/research/
with findings.json. Re-run: `python run_pipeline.py exp01_continuous_9R` /
`exp02_supervised_9R`; `python -m experiments.exp04_multiband_watchlist`.

## 6. Honest limitations
- "Critical" is an operational proxy (hard >= 30mm), not a confirmed safety event
  — no such labels exist.
- Small positive counts (22 at 9m; 36 across bands) make metrics directional, not
  precise.
- Ride quality / derailment dynamics are untested; exp03's jaggedness null is for
  amplitude-escalation only.

