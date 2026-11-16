"""Sanity tests - run with `python tests/test_pipeline.py` (pytest also works)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench import dsp, metrics, perturb  # noqa: E402
from bench.datasets import make_synthetic  # noqa: E402
from bench.models.template_baseline import TemplateBaseline  # noqa: E402
from bench.record import Record  # noqa: E402
from bench.runner import _windows, run_record, stitch  # noqa: E402


def test_rpeak_detector_on_known_beats():
    rec = make_synthetic(duration=60, fs=250, hr=75, noise=0.02)
    r = dsp.detect_rpeaks(rec.ecg, rec.ecg_fs) / rec.ecg_fs
    truth = np.asarray(rec.meta["r_times"])
    truth = truth[(truth > 0.3) & (truth < 59.5)]
    pairs, fn, fp = metrics.match_peaks(truth * 250, r * 250, tol=0.05 * 250)
    assert fn == 0 and fp <= 1, (fn, fp)
    assert np.median([abs(a - b) for a, b in pairs]) / 250 < 0.01


def test_ppg_peaks_follow_r_by_pat():
    rec = make_synthetic(duration=60, fs=128, hr=70, pat=0.3)
    p = dsp.detect_ppg_peaks(rec.ppg, 128) / 128
    r = np.asarray(rec.meta["r_times"])
    d = [q - r[r < q][-1] for q in p if (r < q).any()]
    assert abs(np.median(d) - (0.3 + 0.12)) < 0.03  # systolic peak = PAT + 120 ms


def test_metrics_perfect_and_shifted():
    rec = make_synthetic(duration=60, fs=128)
    rows, rr = metrics.evaluate(rec.ecg, rec.ecg, 128, compute_fd=False)
    assert all(abs(r["rmse"]) < 1e-9 and r["pearson"] > 0.999 for r in rows)
    assert rr["r_f1"] > 0.99
    shifted = np.r_[np.zeros(6), rec.ecg[:-6]]  # 47 ms late
    rows, rr = metrics.evaluate(shifted, rec.ecg, 128, compute_fd=False)
    lag = np.median([r["best_lag_ms"] for r in rows])
    assert abs(lag - 46.9) < 8.0, lag
    assert np.mean([r["pearson_lag"] for r in rows]) > np.mean([r["pearson"] for r in rows])
    assert np.mean([r["beat_pearson"] for r in rows]) > 0.98     # morphology is timing-invariant
    assert abs(rr["r_timing_median_ms"] - 46.9) < 8.0


def test_frechet_small_cases():
    a = np.array([0.0, 1.0, 0.0])
    assert metrics.frechet(a, a) == 0.0
    assert abs(metrics.frechet(a, a + 0.5) - 0.5) < 1e-12


def test_windowing_and_stitching_roundtrip():
    x = np.sin(np.linspace(0, 40, 1000))
    for L, hop in [(128, 128), (128, 64), (300, 150)]:
        W, s = _windows(x, L, hop)
        y = stitch(W, s, len(x), taper=0.0 if hop == L else 0.5)
        assert np.allclose(y, x), (L, hop)


def test_record_roundtrip(tmp=Path("/tmp/_bench_rec.npz")):
    rec = make_synthetic(duration=20)
    rec.extras["acc"] = {"data": np.ones((10, 3)), "fs": 1.0}
    rec.save(tmp)
    r2 = Record.load(tmp)
    assert np.allclose(r2.ecg, rec.ecg) and r2.extras["acc"]["fs"] == 1.0 and r2.meta["pat"] == rec.meta["pat"]


def test_template_baseline_calibrates_and_tracks_rhythm():
    recs = [make_synthetic(subject=str(i), duration=90, pat=0.22, seed=i) for i in range(2)]
    tb = TemplateBaseline(pat=0.0)
    pat = tb.fit(recs)
    assert abs(pat - (0.22 + 0.12)) < 0.03, pat
    ro = run_record(tb, make_synthetic(duration=90, pat=0.22, seed=9), overlap=0.5)
    rows, rr = metrics.evaluate(ro.pred, ro.true, ro.fs, compute_fd=False)
    assert rr["r_f1"] > 0.95 and np.nanmean([r["hr_ae"] for r in rows]) < 2.0


def test_perturbations_preserve_length_and_snr():
    rng = np.random.default_rng(0)
    x = make_synthetic(duration=30, fs=64).ppg
    for f in [perturb.gaussian(10), perturb.motion(), perturb.baseline_wander(), perturb.low_rate(25),
              perturb.time_shift(0.2), perturb.dropout(0.1), perturb.invert()]:
        y = f(x, 64.0, rng)
        assert len(y) == len(x), f.__name__
    y = perturb.gaussian(10)(x, 64.0, rng)
    snr = 10 * np.log10(np.var(x) / np.var(y - x))
    assert abs(snr - 10) < 0.5


def test_resample_with_dc_offset_has_no_edge_artifacts():
    rec = make_synthetic(duration=30, fs=500)
    x = rec.ppg - 19000.0
    y = dsp.resample(x, 500, 128)
    assert abs(y[0] - x[0]) < 5 and abs(y[-1] - x[-1]) < 5
    assert len(dsp.detect_ppg_peaks(y, 128)) >= 25


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)


def test_finite_segments_splits_at_long_gaps_only():
    import numpy as np
    from bench.record import Record, finite_segments
    fs, n = 125, 125 * 600
    p, e = np.sin(np.arange(n) / 10.0), np.cos(np.arange(n) / 7.0)
    p[1000:1050] = np.nan                 # 0.4 s: interpolated
    e[30000:31000] = np.nan               # 8 s: cut here
    segs = finite_segments(Record("x", "s1", p, fs, e, fs))
    assert [s.record_id for s in segs] == ["s1__f0", "s1__f1"]
    assert all(np.isfinite(s.ppg).all() and np.isfinite(s.ecg).all() for s in segs)
    clean = Record("x", "s2", np.ones(n), fs, np.ones(n), fs)
    assert finite_segments(clean)[0] is clean
