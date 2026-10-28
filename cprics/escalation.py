"""
exp02: supervised escalation ranking.

The hand-weighted risk score (risk.py) ranks on CURRENT severity only, so it
blind-spots chronic sites that spiked hard and were then tamped: 6 of our 22
critical sites currently sit below 24mm but reached a median of 43.7mm in the
past. This model ranks on two features only -- current_amp (where it is now)
and max_amp (the worst it has ever been) -- so severity *memory* counts.
Growth, volatility, resets and trajectory shape added no ranking signal and/or
overfit at n=22 positives, so they are deliberately left out.

Ordinary logistic regression on standardised features. We store coef, intercept
and the scaler's mean/scale as plain JSON, so a probability is fully traceable:
    z     = (x - mean) / scale
    logit = intercept + coef . z
    proba = 1 / (1 + exp(-logit))

Use loo_escalation_scores(...) for honest out-of-fold numbers to REPORT, and
fit_escalation(...) + escalation_scores(...) to freeze a fit-on-all model and
apply it to new/unlabelled data in production.
"""
from __future__ import annotations
import json
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut, cross_val_predict

FEATURES = ["current_amp", "max_amp"]
CRITICAL_MM = 30.0


def site_labels(isl, critical=CRITICAL_MM):
    """critical = this site's island ever reached the hard threshold."""
    return isl.groupby("site_id")["hard_amplitude"].max().ge(critical)


def _new_model():
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=2000),
    )


def loo_escalation_scores(feats, labels, features=FEATURES):
    """Honest leave-one-site-out probabilities. Returns {site_id: proba}."""
    X = feats[features].values
    y = np.asarray(labels).astype(int)
    oof = cross_val_predict(_new_model(), X, y, cv=LeaveOneOut(),
                            method="predict_proba")[:, 1]
    return dict(zip(feats["site_id"], oof))


def fit_escalation(feats, labels, features=FEATURES):
    """Fit on ALL labelled sites; return an inspectable JSON-able dict."""
    X = feats[features].values
    y = np.asarray(labels).astype(int)
    pipe = _new_model().fit(X, y)
    sc, clf = pipe.named_steps["standardscaler"], pipe.named_steps["logisticregression"]
    return {
        "features": list(features),
        "mean": sc.mean_.tolist(),
        "scale": sc.scale_.tolist(),
        "coef": clf.coef_[0].tolist(),
        "intercept": float(clf.intercept_[0]),
        "n_train": int(len(y)),
        "n_positive": int(y.sum()),
    }


def save_escalation(model, path):
    with open(path, "w") as fh:
        json.dump(model, fh, indent=2)


def load_escalation(path):
    with open(path) as fh:
        return json.load(fh)


def escalation_scores(feats, model):
    """Apply a frozen model. Returns {site_id: proba}."""
    X = feats[model["features"]].values
    z = (X - np.array(model["mean"])) / np.array(model["scale"])
    logit = model["intercept"] + z @ np.array(model["coef"])
    return dict(zip(feats["site_id"], 1.0 / (1.0 + np.exp(-logit))))
