# exp03_multiband_9R  — NEGATIVE RESULT

**Hypothesis (rail-engineer intuition):** a jaggier cyclic top — more short-
wavelength energy co-located with the 9m top — is riskier, and should flag
escalation and/or warn earlier than 9m alone.

**Data:** all five Butterworth bands (4.5/6/9/13.5/18m) are filtered from the
same Top35 L/R signal. Neighbour-band islands co-located to each 9m site by
position (footprint +/- 5m), worst co-located energy per band. Set: 2263 sites,
22 critical (>=3 obs, same as exp02).

## Tests and results
1. **Coverage** — critical sites are broadband, but so are many others:

   | band  | all sites | critical |
   |-------|-----------|----------|
   | 4.5m  | 25%       | 74%      |
   | 6m    | 60%       | 100%     |
   | 13.5m | 65%       | 100%     |
   | 18m   | 53%       | 97%      |

   Broadband-ness tracks feature SIZE, not escalation.
2. **Ranking** (LOO, exp02 scorecard; scale-free features short_frac/off9_frac/
   n_bands): AUPRC 0.853 (base) -> 0.860 (+short_frac) -> 0.854 (full). No lift;
   full set overfits, as in exp02.
3. **Early warning at EQUAL cost** (176-site budget): multiband captured 18/22
   criticals (vs 22/22 for 9m) and gave 27.3% advance (vs 54.5%), rescuing only
   1/10 sudden sites. The naive uniform-18 thresholds had suggested 45%->68%,
   but that was entirely a 3x watchlist-size artifact; per-band equal-selectivity
   thresholds were {4.5:0.7, 6:5.0, 13.5:13.6, 18:12.4}, where 0.7mm for 4.5m is
   essentially noise. Bracketing the result from both sides showed neither naive
   threshold is principled, and at equal budget the effect reverses to worse.

## Verdict
Multi-band texture does not improve 9m cyclic-top screening — not for ranking,
not for early warning at acceptable cost. The bands share one source signal
(Top35), so they are correlated with 9m and add little independent predictive
signal for escalation.

## Caveat
Tested against the escalation target (hard 9m >= 30mm), NOT ride quality or
derailment. The jaggedness intuition is unconfirmed for amplitude-escalation,
not disproven for ride-quality — retestable in ~an afternoon if an outcome
label is ever supplied.

## Method notes
Co-location (footprint +/- 5m, worst-energy) and thresholds are modelling
choices, but the result is robust: multiband is worse on every axis at equal
budget, so no tolerance tweak is likely to flip it. One untested variant — a
supervised model on time-lagged multiband features — is not recommended at 22
positives (overfit risk) and is unlikely to flip a doubly-negative result.

## Files
notebooks/research/10_exp03_multiband.ipynb (self-contained). No pipeline module
or frozen model — nothing promoted, by design. Key numbers:
outputs/exp03_multiband_9R/findings.json.
