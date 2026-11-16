"""Aggregation and ranking.

* Windows -> subject means first, then across subjects, so a 2.5-h DaLiA
  subject does not outweigh an 8-min BIDMC one.
* 95% CIs by bootstrap over subjects.
* Cross-dataset ranking: mean rank per model over (dataset x condition)
  blocks + Friedman test (Demsar 2006). Plot the critical-difference diagram
  from `mean_ranks` when >= 3 models are compared.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

HIGHER_IS_BETTER = {"pearson", "pearson_lag", "beat_pearson", "r_sens", "r_ppv", "r_f1"}
KEYS = ["model", "track", "dataset", "condition", "seen"]


ATTRS = ["fitzpatrick", "ppg_site"]  # per-subject attributes carried through aggregation


def subject_table(windows: pd.DataFrame, records: pd.DataFrame) -> pd.DataFrame:
    """One row per subject. Subjects with several records (e.g. Aurora-BP 30-s files) are averaged."""
    drop = ["t_start"] + KEYS + ["subject"] + ATTRS
    num = windows.select_dtypes("number").columns.difference(drop)
    w = windows.groupby(KEYS + ["subject"], dropna=False)[list(num)].mean().reset_index()
    rnum = records.select_dtypes("number").columns.difference(drop)
    r = records.groupby(KEYS + ["subject"], dropna=False)[list(rnum)].mean().reset_index()
    attrs = [a for a in ATTRS if a in records]
    if attrs:
        r = r.merge(records.groupby(KEYS + ["subject"], dropna=False)[attrs].first().reset_index(),
                    on=KEYS + ["subject"], how="left")
    return w.merge(r, on=KEYS + ["subject"], how="left")


SKIN_GROUPS = {1: "I-II", 2: "I-II", 3: "III-IV", 4: "III-IV", 5: "V-VI", 6: "V-VI"}


def by_skin_tone(subjects: pd.DataFrame, metrics, min_subjects=3) -> pd.DataFrame:
    """Per Fitzpatrick group (I-II / III-IV / V-VI) metrics, subject-level, with bootstrap CIs.

    Adds, per (model, dataset, condition):
      gap_<metric>  = |best-group mean - worst-group mean|; worst_group_<metric> names the worse group
      kw_p_<metric> = Kruskal-Wallis p-value across groups (subject-level values)
    Groups with < min_subjects subjects are reported but flagged `small_n`.
    """
    if "fitzpatrick" not in subjects or subjects["fitzpatrick"].notna().sum() == 0:
        return pd.DataFrame()
    s = subjects[subjects["fitzpatrick"].notna()].copy()
    s["skin_group"] = s["fitzpatrick"].round().astype(int).clip(1, 6).map(SKIN_GROUPS)
    rows = []
    for key, g in s.groupby(["model", "dataset", "condition"]):
        groups = {k: v for k, v in g.groupby("skin_group")}
        extra = {}
        for m in metrics:
            if m not in g:
                continue
            means = {k: v[m].mean() for k, v in groups.items() if v[m].notna().sum() >= min_subjects}
            if len(means) >= 2:
                hib = m in HIGHER_IS_BETTER
                extra[f"gap_{m}"] = (max(means.values()) - min(means.values()))
                extra[f"worst_group_{m}"] = (min if hib else max)(means, key=means.get)
                vals = [v[m].dropna().to_numpy() for k, v in groups.items() if k in means]
                try:
                    extra[f"kw_p_{m}"] = float(stats.kruskal(*vals).pvalue)
                except ValueError:
                    extra[f"kw_p_{m}"] = np.nan
        for sg, v in groups.items():
            row = dict(model=key[0], dataset=key[1], condition=key[2], skin_group=sg, n_subjects=len(v),
                       small_n=len(v) < min_subjects)
            for m in metrics:
                if m in v:
                    row[m] = v[m].mean()
                    lo, hi = bootstrap_ci(v[m])
                    row[f"{m}_ci"] = f"[{lo:.3g}, {hi:.3g}]"
            rows.append({**row, **extra})
    return pd.DataFrame(rows).sort_values(["model", "dataset", "condition", "skin_group"])


def bootstrap_ci(x, n=2000, seed=0):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return tuple(np.percentile(means, [2.5, 97.5]))


def summary(subjects: pd.DataFrame, metrics) -> pd.DataFrame:
    out = []
    for key, g in subjects.groupby(KEYS, dropna=False):
        row = dict(zip(KEYS, key), n_subjects=len(g))
        for m in metrics:
            if m in g:
                row[m] = g[m].mean()
                lo, hi = bootstrap_ci(g[m])
                row[f"{m}_ci"] = f"[{lo:.3g}, {hi:.3g}]"
        out.append(row)
    return pd.DataFrame(out)


def mean_ranks(summ: pd.DataFrame, metric: str):
    piv = summ.pivot_table(index=["dataset", "condition"], columns="model", values=metric)
    piv = piv.dropna(axis=0, how="any")
    asc = metric not in HIGHER_IS_BETTER
    ranks = piv.rank(axis=1, ascending=asc)
    res = dict(metric=metric, n_blocks=len(piv), mean_ranks=ranks.mean().sort_values().to_dict())
    if piv.shape[1] >= 3 and len(piv) >= 2:
        stat, p = stats.friedmanchisquare(*[piv[c].to_numpy() for c in piv.columns])
        k, N = piv.shape[1], len(piv)
        q = {3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164}.get(k, np.nan)
        res.update(friedman_chi2=float(stat), friedman_p=float(p),
                   nemenyi_cd=float(q * np.sqrt(k * (k + 1) / (6 * N))))
    return res
