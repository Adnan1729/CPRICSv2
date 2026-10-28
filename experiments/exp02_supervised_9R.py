"""
exp02_supervised_9R
Same signal processing, islands, tracking and archetypes as exp01 (9m,
9_top_right). The only change: the watchlist is ranked by a supervised
escalation probability (cprics/escalation.py, logistic on current_amp +
max_amp) instead of the hand-weighted risk score. Honest leave-one-site-out
AUPRC rises 0.589 -> 0.853, P@20 0.65 -> 0.75, by recovering chronic sites that
spiked and were tamped. Reuses exp01's frozen archetypes for FP composition
only; archetypes do not affect ranking here.
"""
from experiments.exp01_continuous_9R import PARAMS as _EXP01

NAME = "exp02_supervised_9R"
DESCRIPTION = ("9m 9_top_right; supervised escalation ranking "
               "(logistic on current_amp + max_amp) replacing the risk score")

PARAMS = dict(_EXP01)
PARAMS.update(
    ranking_method="supervised_severity",
    escalation_features=["current_amp", "max_amp"],
    archetypes_experiment="exp01_continuous_9R",
)
