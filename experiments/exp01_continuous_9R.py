"""Experiment 01 — continuous pre-risk on the 9 m right-rail channel (v1 baseline)."""
NAME = "exp01_continuous_9R"
DESCRIPTION = "Wavelength-aware islands + sigmoid-continuous severity, 9 m right rail"

PARAMS = dict(
    channel="9_top_right", wavelength=9,
    severity_method="sigmoid",
    tracking_gap_m=7.0,
    concern_mm=18, critical_mm=30,
    candidate_floor=2.0, sig_centre=5.0, sig_width=1.0,
)
