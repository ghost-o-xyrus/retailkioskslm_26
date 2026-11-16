"""Method 2: information-theoretic coupling between ECG and PPG.

Non-parametric estimators (k-nearest-neighbour, max-norm):
  ksg_mi(x, y)        Kraskov-Stoegbauer-Grassberger estimator 1 of I(X;Y)
  ksg_cmi(x, y, z)    Frenzel-Pompe estimator of I(X;Y|Z)
  transfer_entropy    TE(X->Y) = I(Y_t ; X_past | Y_past)
  gaussian_mi         the linear/Gaussian counterpart, -1/2 log(1 - R^2) (equals Granger for TE)
All in bits. Each estimate is reported with a surrogate baseline (X circularly shifted by a random
lag), so `*_excess` = estimate - surrogate mean is the coupling beyond estimator bias.

info_coefficient(I) = 1 - 2^(-2I) is the R^2 a Gaussian channel with that much information would give,
which makes MI comparable with the R^2 numbers of the probes and the Wiener filter.

For waveforms, high-dimensional MI is not estimable from a few thousand beats, so the waveform-level
information question is answered by the probes (lower bounds) and the forward model (upper bounds).
"""
from __future__ import annotations

import numpy as np
from scipy.special import digamma
from scipy.spatial import cKDTree

LN2 = np.log(2.0)


def _prep(a, rng):
    a = np.asarray(a, float)
    a = a.reshape(len(a), -1)
    a = (a - a.mean(0)) / np.where(a.std(0) > 0, a.std(0), 1.0)
    return a + 1e-10 * rng.standard_normal(a.shape)  # break ties (intervals are quantised)


def ksg_mi(x, y, k=4, seed=0):
    rng = np.random.default_rng(seed)
    x, y = _prep(x, rng), _prep(y, rng)
    n = len(x)
    xy = np.c_[x, y]
    eps = cKDTree(xy).query(xy, k=k + 1, p=np.inf)[0][:, -1]
    r = np.nextafter(eps, 0)
    nx = cKDTree(x).query_ball_point(x, r, p=np.inf, return_length=True) - 1
    ny = cKDTree(y).query_ball_point(y, r, p=np.inf, return_length=True) - 1
    return max(0.0, (digamma(k) + digamma(n) - np.mean(digamma(nx + 1) + digamma(ny + 1))) / LN2)


def ksg_cmi(x, y, z, k=4, seed=0):
    rng = np.random.default_rng(seed)
    x, y, z = _prep(x, rng), _prep(y, rng), _prep(z, rng)
    xyz = np.c_[x, y, z]
    eps = cKDTree(xyz).query(xyz, k=k + 1, p=np.inf)[0][:, -1]
    r = np.nextafter(eps, 0)
    cnt = lambda a: cKDTree(a).query_ball_point(a, r, p=np.inf, return_length=True) - 1
    nxz, nyz, nz = cnt(np.c_[x, z]), cnt(np.c_[y, z]), cnt(z)
    return max(0.0, (digamma(k) - np.mean(digamma(nxz + 1) + digamma(nyz + 1) - digamma(nz + 1))) / LN2)


def transfer_entropy(x, y, hist=2, k=4, seed=0):
    """TE(X->Y): information the past of X adds about Y_t beyond Y's own past (bits)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    yt = y[hist:]
    ypast = np.stack([y[hist - j - 1:len(y) - j - 1] for j in range(hist)], axis=1)
    xpast = np.stack([x[hist - j - 1:len(x) - j - 1] for j in range(hist)], axis=1)
    return ksg_cmi(yt, xpast, ypast, k=k, seed=seed)


def gaussian_mi(x, y):
    x = np.asarray(x, float).reshape(len(x), -1)
    y = np.asarray(y, float).reshape(len(y), -1)
    c = np.cov(np.c_[x, y].T)
    dx = x.shape[1]
    num = np.linalg.slogdet(c[:dx, :dx])[1] + np.linalg.slogdet(c[dx:, dx:])[1]
    return max(0.0, 0.5 * (num - np.linalg.slogdet(c)[1]) / LN2)


def gaussian_te(x, y, hist=2):
    x, y = np.asarray(x, float), np.asarray(y, float)
    yt = y[hist:]
    yp = np.stack([y[hist - j - 1:len(y) - j - 1] for j in range(hist)], axis=1)
    xp = np.stack([x[hist - j - 1:len(x) - j - 1] for j in range(hist)], axis=1)
    def resid_var(A):
        A1 = np.c_[np.ones(len(A)), A]
        beta = np.linalg.lstsq(A1, yt, rcond=None)[0]
        return np.var(yt - A1 @ beta)
    return max(0.0, 0.5 * np.log(resid_var(yp) / resid_var(np.c_[yp, xp])) / LN2)


def info_coefficient(bits):
    return 1.0 - 2.0 ** (-2.0 * np.asarray(bits, float))


def with_surrogate(fn, x, y, n_surr=20, min_shift=20, seed=0, **kw):
    """Estimate fn(x, y) and the same with x circularly shifted (destroys x-y coupling, keeps
    each series' own dynamics). Returns (estimate, surrogate mean, p-value)."""
    rng = np.random.default_rng(seed)
    est = fn(x, y, **kw)
    n = len(x)
    if n < 3 * min_shift:
        return est, np.nan, np.nan
    surr = [fn(np.roll(x, int(rng.integers(min_shift, n - min_shift))), y, **kw) for _ in range(n_surr)]
    return est, float(np.mean(surr)), float((1 + np.sum(np.asarray(surr) >= est)) / (n_surr + 1))


def interval_coupling(rr, pp, hist=2, k=4, n_surr=20, seed=0):
    """All interval-level information measures for one record (RR from ECG, PP from PPG, matched)."""
    rr, pp = np.asarray(rr, float), np.asarray(pp, float)
    drr, dpp = np.diff(rr), np.diff(pp)
    out = {"n_beats": len(rr)}
    for name, fn, a, b in [("mi_rr_pp", ksg_mi, rr, pp), ("mi_drr_dpp", ksg_mi, drr, dpp),
                           ("te_rr_to_pp", lambda x, y, **kw: transfer_entropy(x, y, hist=hist, **kw), rr, pp),
                           ("te_pp_to_rr", lambda x, y, **kw: transfer_entropy(x, y, hist=hist, **kw), pp, rr)]:
        est, s, p = with_surrogate(fn, a, b, n_surr=n_surr, seed=seed, k=k)
        out.update({name: est, f"{name}_surr": s, f"{name}_excess": est - s if np.isfinite(s) else np.nan,
                    f"{name}_p": p})
    out["gmi_rr_pp"] = gaussian_mi(rr, pp)
    out["gmi_drr_dpp"] = gaussian_mi(drr, dpp)
    out["gte_rr_to_pp"] = gaussian_te(rr, pp, hist)
    out["gte_pp_to_rr"] = gaussian_te(pp, rr, hist)
    out["r2eq_drr_dpp"] = float(info_coefficient(out["mi_drr_dpp_excess"])) if np.isfinite(out["mi_drr_dpp_excess"]) else np.nan
    return out
