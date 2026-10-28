# exp02_supervised_9R

**Technique:** supervised escalation ranking. Replace the hand-weighted risk
score with a 2-feature logistic regression (current_amp + max_amp) producing a
per-site escalation probability used to order the watchlist. Everything else
(signal processing, islands, tracking, archetypes) is identical to exp01.

**Validation:** leave-one-site-out (22 positives / 2263 sites). Reported numbers
are out-of-fold. Shipped model (models/exp02_supervised_9R_model.json) is fit on
all sites for applying to future/unlabelled data.

## Result vs exp01 (ranking only; watchlist composition unchanged)

| metric | exp01 risk | exp02 supervised |
|---|---|---|
| AUPRC | 0.589 | 0.853 |
| P@20  | 0.65  | 0.75 |
| R@20  | 0.591 | 0.682 |
| P@50  | 0.34  | 0.44 |
| R@50  | 0.773 | 1.00 |

**Operational headline:** all 22 critical sites fall in the top 50 of the
91-site watchlist (15 in the top 20). The list can be worked down to 50 with no
loss of critical coverage — ~2.3 flags per critical vs 4.14 over the full list.
Unchanged watchlist composition: 91 flagged, recall 1.0, precision 0.242,
advance 54.5%, median lead 12 months, 69 false positives (34 steady climber /
34 saw-tooth / 1 severe).

## Why it works 
The risk score sees only CURRENT state. 6 of the 22 critical sites currently sit
below 24mm but reached a median historical peak of 43.7mm — chronic sites that
spiked and were tamped. max_amp is the island's memory of past severity (known
at ranking time, not future info) and recovers them. Evidence it's real skill,
not label overlap: the P@50 and R@50 lift is deeper than the easy top of the
list, and the recovered sites are genuine chronic liabilities.

## Frozen model (standardised logistic)
features [current_amp, max_amp]; coef [1.23, 3.06]; intercept -13.16.
max_amp carries ~2.5x the weight of current_amp — the model leans on severity
memory, as the mechanism predicts.

## Negative results (recorded, not discarded)
- Trajectory shape/speed adds nothing: behaviour-only AUPRC 0.586 (~= baseline
  0.589); growth lifts current-only 0.682 -> 0.684 only.
- More features overfit at n=22: 7-feature model 0.783 < 2-feature 0.853.
- Signal is severity (current + historical peak), full stop.

## Caveats
LOO AUPRC at 22 positives is noisy; the robust claims are the direction and
mechanism (severity memory), not the exact 0.853. Feature set chosen by
motivated hypothesis (calm-site analysis), not leaderboard search.

## Reproduce
`python run_pipeline.py exp02_supervised_9R`
Config: experiments/exp02_supervised_9R.py · Model: cprics/escalation.py
Frozen: models/exp02_supervised_9R_model.json
Outputs: outputs/exp02_supervised_9R/ (watchlist.xlsx, metrics.json)
