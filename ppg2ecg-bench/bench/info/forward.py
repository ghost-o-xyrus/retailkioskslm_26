"""Method 3: electro -> mechano -> hemodynamic -> optical forward model, and identifiability.

Question: if the ECG changes in a given way (longer QT, wider QRS, longer PR, ST deviation,
weaker P wave), how much does the PPG change, and can that change be told apart from the normal
spread of everything else that shapes the pulse (transit time, stroke volume, compliance, wave
reflection, tissue optics) and from measurement noise?

Chain (one steady beat, periodic):
  ECG parameters theta: hr, pr_ms, qrs_ms, qt_ms, st_mm, p_amp
      | electromechanical coupling (PEP, LVET, stroke volume, atrial kick)   <- COUPLING dict
  aortic flow Q(t)  (skewed half-sine of duration LVET carrying stroke volume SV)
      | 3-element Windkessel (Zc, R, C)
  aortic pressure -> transit delay PTT + reflected wave -> tissue/sensor low-pass -> optical gain
  PPG(t), observed WITHOUT the ECG (time origin unknown: absorbed by PTT).

Identifiability: Jacobian J = dPPG/d[theta, nu] by central differences, Fisher information
F = N * J^T J / sigma^2 for N beats with white noise sigma (set from beat-level PPG SNR), Gaussian
population priors on the nuisances nu (and, in the realistic case, on the other ECG parameters).
The Cramer-Rao bound sd(theta_i) = sqrt([F^-1]_ii) is the best any unbiased estimator - including
any neural network - could do under this model. Comparing it with the clinically relevant change
(e.g. 60 ms of QT) says whether that change is identifiable from the PPG in principle.

IMPORTANT. The coupling coefficients and nuisance spreads below are first-pass literature-informed
placeholders, documented one by one, to be calibrated (Pulse Wave Database [Charlton 2019] for the
arterial part; PEP/LVET/EMW literature for coupling). Results are only as good as these numbers, so
the module reports a sweep over each coupling coefficient instead of a single verdict.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import signal as sps

# ------------------------------------------------------------------ defaults (all documented)
THETA0 = dict(hr=70.0, pr_ms=160.0, qrs_ms=90.0, qt_ms=400.0, st_mm=0.0, p_amp=1.0)
THETA_PRIOR_SD = dict(hr=12.0, pr_ms=25.0, qrs_ms=12.0, qt_ms=30.0, st_mm=0.5, p_amp=0.3)
CLINICAL_DELTA = dict(hr=5.0,        # ANSI/AAMI EC13 heart-rate accuracy (+-5 bpm)
                      pr_ms=40.0,    # 160 -> 200 ms = first-degree AV block threshold
                      qrs_ms=20.0,   # 100 -> 120 ms = bundle-branch block threshold
                      qt_ms=60.0,    # QTc prolongation > 60 ms = drug-safety alarm
                      st_mm=1.0,     # 1 mm ST elevation = STEMI criterion (limb leads)
                      p_amp=0.5)     # loss of half the atrial signal (relative)

NU0 = dict(ptt_ms=200.0, lvet_off_ms=0.0, sv0_ml=70.0, contractility=1.0, C=1.4, R=1.0, Zc=0.05,
           refl_gain=0.35, refl_delay_ms=140.0, lp_hz=6.0, gain=1.0)
NU_PRIOR_SD = dict(ptt_ms=1e4,        # time origin: WITHOUT an ECG the absolute pulse timing carries no
                                      # information (PEP + PTT are unobservable), so effectively no prior
                   lvet_off_ms=15.0,  # person-to-person LVET spread at a given HR (Weissler regression SE)
                   sv0_ml=15.0, contractility=0.15,
                   C=0.4, R=0.2, Zc=0.015,      # ranges of the PWDB virtual cohort, approx.
                   refl_gain=0.10, refl_delay_ms=40.0,
                   lp_hz=1.5,                    # tissue / sensor smoothing
                   gain=0.3)                     # optical gain (contact pressure, perfusion, melanin)

COUPLING = dict(
    pep0_ms=95.0,          # pre-ejection period at 70 bpm (normal 80-120 ms)
    pep_hr=-0.4,           # ms per bpm: PEP shortens slightly with rate
    pep_qrs=0.5,           # ms PEP per ms QRS: dyssynchrony (LBBB) lengthens PEP
    pep_contr=-60.0,       # ms per unit contractility: stronger contraction -> shorter PEP
    lvet_hr=-1.7,          # Weissler: LVET = 413 - 1.7 HR (ms)
    lvet_qt=0.5,           # fraction of a QT change carried into LVET (electromechanical window;
                           # ~1 if systole tracks T-end, <1 in long-QT where EMW turns negative)
    kick_frac=0.20,        # atrial contribution to stroke volume (15-25 %)
    pr_opt_ms=160.0, pr_width_ms=120.0,   # AV-delay optimum and tolerance of the atrial kick
    k_p=0.0,               # stroke-volume change per unit P amplitude (no direct link assumed)
    k_st=0.0,              # fraction of contractility lost per mm ST deviation (ischaemia proxy);
                           # 0 = ST has no mechanical consequence; the sweep explores 0.02-0.10
)

FS_SIM = 1000.0
FS_OBS = 128.0
OBS_S = 2.0


@dataclass
class ForwardModel:
    coupling: dict = field(default_factory=lambda: dict(COUPLING))
    snr_db: float = 20.0          # beat-level PPG SNR (pulse RMS / residual RMS)

    # --------------------------------------------------------------- mechanics
    def mechanics(self, th, nu):
        c = self.coupling
        contr = nu["contractility"] * max(0.0, 1.0 - c["k_st"] * abs(th["st_mm"]))
        pep = (c["pep0_ms"] + c["pep_hr"] * (th["hr"] - 70.0) + c["pep_qrs"] * (th["qrs_ms"] - 90.0)
               + c["pep_contr"] * (contr - 1.0))
        qt_expected = 400.0 * np.sqrt(70.0 / th["hr"])          # Bazett-scaled reference
        lvet = (413.0 + c["lvet_hr"] * th["hr"] + c["lvet_qt"] * (th["qt_ms"] - qt_expected)
                + nu["lvet_off_ms"])
        kick = c["kick_frac"] * np.exp(-((th["pr_ms"] - c["pr_opt_ms"]) / c["pr_width_ms"]) ** 2)
        kick *= max(0.0, 1.0 + c["k_p"] * (th["p_amp"] - 1.0))
        sv = nu["sv0_ml"] * contr * (1.0 - c["kick_frac"] + kick)
        return dict(pep_ms=pep, lvet_ms=max(150.0, lvet), sv_ml=max(5.0, sv))

    # --------------------------------------------------------------- one periodic beat -> PPG
    def simulate(self, th, nu, n_beats=6):
        m = self.mechanics(th, nu)
        rr = 60.0 / th["hr"]
        n_rr = int(round(rr * FS_SIM))
        t = np.arange(n_rr) / FS_SIM
        onset = (-0.4 * th["qrs_ms"] + m["pep_ms"]) / 1000.0          # ejection start, R at t=0
        # the flow pulse is built starting at t=0 and delayed by `onset` together with the transit
        # time at the end, so timing enters through ONE exact fractional shift
        u = t / (m["lvet_ms"] / 1000.0)
        shape = np.where((u >= 0) & (u <= 1), np.sin(np.pi * np.clip(u, 0, 1)) * np.exp(-1.2 * np.clip(u, 0, 1)), 0.0)
        q = shape / max(shape.sum() / FS_SIM, 1e-9) * m["sv_ml"]       # ml/s, integral = SV
        Q = np.tile(q, n_beats)
        # 3-element Windkessel: C dPc/dt = Q - Pc/R ; P = Pc + Zc Q   (exact discretisation)
        a = np.exp(-1.0 / (FS_SIM * nu["R"] * nu["C"]))
        pc = sps.lfilter([(1 - a) * nu["R"]], [1, -a], Q)
        p = pc + nu["Zc"] * Q
        p = p[-n_rr:]                                                # periodic steady state, 1 beat
        p = p - p.mean()
        T = n_rr / FS_SIM
        tt = np.arange(n_rr) / FS_SIM
        # fractional periodic delay (np.roll would quantise delays to whole samples, and finite
        # differences would then fail to cancel a pure time shift)
        sh = lambda x, ms: np.interp((tt - ms / 1000.0) % T, tt, x, period=T)
        ps = p + nu["refl_gain"] * sh(p, nu["refl_delay_ms"])
        b, a2 = sps.butter(2, nu["lp_hz"] / (FS_SIM / 2))
        ps = sps.filtfilt(b, a2, np.tile(ps, 5))[2 * n_rr:3 * n_rr]
        ppg = nu["gain"] * ps / 40.0                                  # ~unit amplitude at defaults
        # observe OBS_S seconds at FS_OBS, delayed by the transit time (periodic continuation)
        t_obs = np.arange(int(OBS_S * FS_OBS)) / FS_OBS
        delay = onset + nu["ptt_ms"] / 1000.0
        return np.interp((t_obs - delay) % T, tt, ppg, period=T)

    # --------------------------------------------------------------- Fisher information
    def jacobian(self, th, nu, names):
        allp = {**th, **nu}
        J = []
        for k in names:
            sd = THETA_PRIOR_SD.get(k, NU_PRIOR_SD.get(k))
            h = 0.02 * min(sd, 40.0)
            up, dn = dict(allp), dict(allp)
            up[k] += h
            dn[k] -= h
            split = lambda d: ({x: d[x] for x in th}, {x: d[x] for x in nu})
            J.append((self.simulate(*split(up)) - self.simulate(*split(dn))) / (2 * h))
        return np.stack(J, axis=1)

    def noise_sigma(self, th, nu):
        y = self.simulate(th, nu)
        return np.sqrt(np.mean((y - y.mean()) ** 2)) / 10 ** (self.snr_db / 20.0)

    def crlb(self, th=None, nu=None, n_beats=(1, 10, 100, 1000), mode="new_person", drift=0.3):
        """Bound per ECG parameter in three information settings:
             oracle      everything else known exactly (pure sensitivity / noise limit)
             nuisance    hemodynamic nuisances unknown (prior), other ECG params known
             realistic   nuisances AND the other ECG params unknown (priors)
        mode='new_person': population priors (screening a stranger).
        mode='tracking'  : the person's own baseline is known up to slow drift - priors shrink to
                           drift x population sd (detecting a CHANGE in someone already monitored).
        The time origin (ptt_ms) stays unknown in both modes: there is no ECG."""
        th, nu = dict(THETA0, **(th or {})), dict(NU0, **(nu or {}))
        scale = 1.0 if mode == "new_person" else drift
        tn, nn = list(th), list(nu)
        J = self.jacobian(th, nu, tn + nn)
        s2 = self.noise_sigma(th, nu) ** 2
        F1 = J.T @ J / s2
        prior = np.array([1 / (scale * THETA_PRIOR_SD[k]) ** 2 for k in tn]
                         + [1 / ((scale if k != "ptt_ms" else 1.0) * NU_PRIOR_SD[k]) ** 2 for k in nn])
        rows = []
        for i, k in enumerate(tn):
            for N in n_beats:
                F = N * F1
                oracle = 1 / np.sqrt(F[i, i]) if F[i, i] > 0 else np.inf
                idx = [i] + [len(tn) + j for j in range(len(nn))]
                Fn = F[np.ix_(idx, idx)] + np.diag(np.r_[0.0, prior[len(tn):]])
                Fr = F + np.diag(np.r_[[0.0 if j == i else prior[j] for j in range(len(tn))], prior[len(tn):]])
                bound = lambda M, pos: np.sqrt(np.linalg.pinv(M)[pos, pos]) if M[pos, pos] > 0 else np.inf
                nuis, real = bound(Fn, 0), bound(Fr, i)
                d = CLINICAL_DELTA[k]
                rows.append(dict(param=k, mode=mode, operating_point=th[k], n_beats=N, oracle_sd=oracle, nuisance_sd=nuis, realistic_sd=real,
                                 clinical_delta=d, detectable_realistic=bool(real < d / 2),
                                 dprime_realistic=d / real if real > 0 else np.inf))
        return pd.DataFrame(rows)

    def sensitivity(self, th=None, nu=None):
        """|dPPG/dtheta| x clinical delta, relative to noise: how big a clinically relevant ECG change
        looks in the PPG, before any confounding (per beat)."""
        th, nu = dict(THETA0, **(th or {})), dict(NU0, **(nu or {}))
        J = self.jacobian(th, nu, list(th))
        s = self.noise_sigma(th, nu)
        return pd.DataFrame([dict(param=k, ppg_change_rms_per_delta=float(np.sqrt(np.mean((J[:, i] * CLINICAL_DELTA[k]) ** 2))),
                                  snr_of_change_1beat=float(np.sqrt(np.sum((J[:, i] * CLINICAL_DELTA[k]) ** 2)) / s))
                             for i, k in enumerate(th)])


# operating points: derivatives vanish at symmetric points by construction (|ST| at 0, the AV-delay
# optimum), so each parameter is evaluated where a clinical question is actually asked.
OPERATING_POINTS = dict(hr=[70.0], pr_ms=[160.0, 220.0], qrs_ms=[90.0, 130.0], qt_ms=[400.0, 480.0],
                        st_mm=[0.5, 2.0], p_amp=[1.0, 0.5])


def crlb_grid(fm, n_beats=(1, 10, 100, 1000), modes=("new_person", "tracking")):
    out = []
    for k, vals in OPERATING_POINTS.items():
        for v in vals:
            for mode in modes:
                r = fm.crlb(th={k: v}, n_beats=n_beats, mode=mode)
                out.append(r[r.param == k])
    return pd.concat(out, ignore_index=True)


def coupling_sweep(param, values, coupling_key, n_beats=100, mode="tracking", point=None, **kw):
    """Realistic CRLB of one ECG parameter as one coupling coefficient varies (e.g. ST vs k_st)."""
    rows = []
    point = point if point is not None else OPERATING_POINTS[param][-1]
    for v in values:
        fm = ForwardModel(coupling=dict(COUPLING, **{coupling_key: v}), **kw)
        r = fm.crlb(th={param: point}, n_beats=(n_beats,), mode=mode)
        r = r[r.param == param].iloc[0].to_dict()
        r["coupling"] = coupling_key
        r["coupling_value"] = v
        rows.append(r)
    return pd.DataFrame(rows)


def default_report(snr_db=20.0):
    fm = ForwardModel(snr_db=snr_db)
    grid = crlb_grid(fm)
    sens = pd.concat([fm.sensitivity(th={k: v[-1]}).query("param == @k") for k, v in OPERATING_POINTS.items()],
                     ignore_index=True)
    sweeps = pd.concat([
        coupling_sweep("st_mm", [0.0, 0.02, 0.05, 0.10], "k_st", snr_db=snr_db),
        coupling_sweep("qt_ms", [0.0, 0.25, 0.5, 1.0], "lvet_qt", snr_db=snr_db),
        coupling_sweep("qrs_ms", [0.0, 0.25, 0.5, 1.0], "pep_qrs", snr_db=snr_db),
        coupling_sweep("p_amp", [0.0, 0.25, 0.5], "k_p", snr_db=snr_db),
        coupling_sweep("pr_ms", [0.10, 0.20, 0.30], "kick_frac", snr_db=snr_db),
    ], ignore_index=True)
    return grid, sens, sweeps
