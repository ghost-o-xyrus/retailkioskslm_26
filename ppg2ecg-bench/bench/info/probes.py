"""Method 5: machine-learning probes - what does the PPG measurably carry about each ECG feature?

For every ECG target (RR, QRS width, PR, P amplitude, ST level, T amplitude, QT, QTc, ...) we fit
predictors from three nested PPG feature sets:
    rate    pulse rate only
    timing  rate + pulse-interval variability (what a beat detector gives)
    full    timing + pulse morphology (shape, widths, areas, DCT of pulse and its derivative)
under three evaluation schemes:
    between       GroupKFold by subject: a NEW person (the deployment case)
    personalized  first 70% of each subject's blocks train, last 30% test (subject seen in training)
    within_change as personalized, but targets and features are deviations from the subject's
                  training mean: does the PPG track CHANGES of the feature inside a person?
Outputs per target x set x scheme x model: R^2 (95% CI by bootstrapping subjects), the gain of each
richer set over the poorer one (paired bootstrap), the split-half noise ceiling of the target, and
an information lower bound I >= -1/2 log2(1 - R^2) bits (exact for Gaussian targets/errors).

Reading the output: if `full` is no better than `rate` for QT, the PPG carries no QT information
beyond what heart rate implies; if `between` << `personalized`, a model "knows" a feature only by
recognising the person.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, RidgeCV
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from .beats import ECG_TARGETS, RATE_FEATURES, TIMING_FEATURES, morph_feature_names

FEATURE_SETS = {"rate": RATE_FEATURES,
                "timing": TIMING_FEATURES + ["hr_ppg"],
                "full": TIMING_FEATURES + ["hr_ppg"] + morph_feature_names()}
SCHEMES = ("between", "personalized", "within_change")


def _models(kind="reg"):
    if kind == "reg":
        return {"ridge": lambda: make_pipeline(SimpleImputer(), StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13))),
                "hgb": lambda: HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                                             min_samples_leaf=20, l2_regularization=1.0, random_state=0)}
    return {"logit": lambda: make_pipeline(SimpleImputer(), StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)),
            "hgb": lambda: HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15,
                                                          min_samples_leaf=20, random_state=0)}


def _r2(y, p):
    v = np.var(y)
    return 1 - np.mean((y - p) ** 2) / v if v > 0 else np.nan


def oof_predictions(df, target, feats, scheme, make_model, n_splits=5, min_blocks_subject=6):
    """Out-of-fold predictions. Returns (y, pred, subject) for the evaluated rows."""
    d = df[["subject", target] + feats].dropna(subset=[target]).copy()
    d = d.sort_index()
    y = d[target].to_numpy(float)
    X = d[feats].to_numpy(float)
    g = d["subject"].astype(str).to_numpy()
    pred = np.full(len(y), np.nan)
    yy = y.copy()
    if scheme == "between":
        n_g = len(np.unique(g))
        if n_g < 3:
            return None
        for tr, te in GroupKFold(n_splits=min(n_splits, n_g)).split(X, y, g):
            m = make_model().fit(X[tr], y[tr])
            pred[te] = m.predict(X[te])
    else:
        tr_idx, te_idx = [], []
        for s in np.unique(g):
            ids = np.flatnonzero(g == s)          # rows already in time order within subject
            if len(ids) < min_blocks_subject:
                continue
            k = int(0.7 * len(ids))
            tr_idx.append(ids[:k]), te_idx.append(ids[k:])
        if len(tr_idx) < 3:
            return None
        tr, te = np.concatenate(tr_idx), np.concatenate(te_idx)
        Xs, ys = X.copy(), y.copy()
        if scheme == "within_change":
            for a, b in zip(tr_idx, te_idx):
                mx, my = np.nanmean(X[a], axis=0), y[a].mean()
                Xs[np.r_[a, b]] = X[np.r_[a, b]] - mx
                ys[np.r_[a, b]] = y[np.r_[a, b]] - my
        m = make_model().fit(Xs[tr], ys[tr])
        pred[te] = m.predict(Xs[te])
        yy = ys
    ok = np.isfinite(pred)
    return yy[ok], pred[ok], g[ok]


def _boot_r2(y, p, g, n_boot=500, seed=0):
    rng = np.random.default_rng(seed)
    subj = np.unique(g)
    idx = {s: np.flatnonzero(g == s) for s in subj}
    vals = []
    for _ in range(n_boot):
        pick = np.concatenate([idx[s] for s in rng.choice(subj, len(subj), replace=True)])
        vals.append(_r2(y[pick], p[pick]))
    return np.nanpercentile(vals, [2.5, 97.5])


def noise_ceiling(df, target, scheme):
    """Spearman-Brown corrected split-half reliability of the target (odd vs even beats)."""
    a, b = df.get(f"{target}__half1"), df.get(f"{target}__half2")
    if a is None or b is None:
        return np.nan
    d = pd.DataFrame({"a": a, "b": b, "s": df["subject"].astype(str)}).dropna()
    if len(d) < 10:
        return np.nan
    if scheme == "within_change":
        d["a"] -= d.groupby("s")["a"].transform("mean")
        d["b"] -= d.groupby("s")["b"].transform("mean")
    r = np.corrcoef(d["a"], d["b"])[0, 1]
    return float(2 * r / (1 + r)) if r > -1 else np.nan


def variance_split(df, target):
    d = df[["subject", target]].dropna()
    if d["subject"].nunique() < 2:
        return np.nan, np.nan
    within = d.groupby("subject")[target].var().mean()
    between = d.groupby("subject")[target].mean().var()
    return float(np.sqrt(between)), float(np.sqrt(within))


def run_probes(df, targets=None, schemes=SCHEMES, n_boot=300, models=("ridge", "hgb")):
    targets = [t for t in (targets or ECG_TARGETS) if t in df and df[t].notna().sum() >= 50]
    mk = _models("reg")
    rows = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for t in targets:
            sd_b, sd_w = variance_split(df, t)
            for scheme in schemes:
                ceil = noise_ceiling(df, t, scheme)
                preds = {}
                for fs_name, feats in FEATURE_SETS.items():
                    feats = [f for f in feats if f in df]
                    for mname in models:
                        res = oof_predictions(df, t, feats, scheme, mk[mname])
                        if res is None:
                            continue
                        y, p, g = res
                        preds[(fs_name, mname)] = res
                        r2 = _r2(y, p)
                        lo, hi = _boot_r2(y, p, g, n_boot=n_boot)
                        rows.append(dict(target=t, scheme=scheme, features=fs_name, model=mname, n_blocks=len(y),
                                         n_subjects=len(np.unique(g)), r2=r2, r2_lo=lo, r2_hi=hi,
                                         noise_ceiling=ceil, r2_over_ceiling=r2 / ceil if ceil and ceil > 0 else np.nan,
                                         info_lb_bits=-0.5 * np.log2(1 - r2) if 0 < r2 < 1 else 0.0,
                                         target_sd_between=sd_b, target_sd_within=sd_w))
                # paired gains: full - timing, timing - rate (same rows, same model)
                for mname in models:
                    for hi_set, lo_set in (("full", "timing"), ("timing", "rate"), ("full", "rate")):
                        a, b = preds.get((hi_set, mname)), preds.get((lo_set, mname))
                        if a is None or b is None or len(a[0]) != len(b[0]):
                            continue
                        y, pa, g = a
                        pb = b[1]
                        rng = np.random.default_rng(1)
                        subj = np.unique(g)
                        idx = {s: np.flatnonzero(g == s) for s in subj}
                        gains = []
                        for _ in range(n_boot):
                            pick = np.concatenate([idx[s] for s in rng.choice(subj, len(subj), replace=True)])
                            gains.append(_r2(y[pick], pa[pick]) - _r2(y[pick], pb[pick]))
                        rows.append(dict(target=t, scheme=scheme, features=f"gain:{hi_set}-{lo_set}", model=mname,
                                         n_blocks=len(y), n_subjects=len(subj), r2=_r2(y, pa) - _r2(y, pb),
                                         r2_lo=np.nanpercentile(gains, 2.5), r2_hi=np.nanpercentile(gains, 97.5)))
    return pd.DataFrame(rows)


def run_class_probe(df, label="af", n_boot=300):
    """Rhythm screening probe (e.g. AF vs not, per block) from rate / timing / full PPG features,
    always between-subject. AUC with subject-bootstrap CI."""
    if label not in df or df[label].nunique() < 2:
        return pd.DataFrame()
    rows = []
    mk = _models("clf")
    d = df.dropna(subset=[label])
    g = d["subject"].astype(str).to_numpy()
    y = d[label].astype(int).to_numpy()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for fs_name, feats in FEATURE_SETS.items():
            X = d[[f for f in feats if f in d]].to_numpy(float)
            for mname, make in mk.items():
                p = np.full(len(y), np.nan)
                n_g = len(np.unique(g))
                for tr, te in GroupKFold(n_splits=min(5, n_g)).split(X, y, g):
                    if len(np.unique(y[tr])) < 2:
                        continue
                    p[te] = make().fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
                ok = np.isfinite(p)
                auc = roc_auc_score(y[ok], p[ok])
                rng = np.random.default_rng(0)
                subj = np.unique(g[ok])
                idx = {s: np.flatnonzero(g[ok] == s) for s in subj}
                boots = []
                for _ in range(n_boot):
                    pick = np.concatenate([idx[s] for s in rng.choice(subj, len(subj), replace=True)])
                    if len(np.unique(y[ok][pick])) == 2:
                        boots.append(roc_auc_score(y[ok][pick], p[ok][pick]))
                rows.append(dict(label=label, features=fs_name, model=mname, auc=auc,
                                 auc_lo=np.percentile(boots, 2.5), auc_hi=np.percentile(boots, 97.5),
                                 n_blocks=int(ok.sum()), n_subjects=len(subj), prevalence=float(y[ok].mean())))
    return pd.DataFrame(rows)
