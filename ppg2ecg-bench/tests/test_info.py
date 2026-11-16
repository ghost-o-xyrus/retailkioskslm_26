"""Tests for the Track 1.5 information-transfer analysis (run: python tests/test_info.py, or pytest)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.datasets import make_synthetic, synth_beat  # noqa: E402
from bench.info import agreement, beats, coherence, forward, infotheory  # noqa: E402


def test_delineation_recovers_synthetic_intervals():
    t = np.arange(-beats.PRE, beats.POST, 1 / beats.FS)
    f = beats.delineate(synth_beat(t, 0.857), 0.857)
    assert 95 <= f["qrs_ms"] <= 125          # Gaussians at +-35 ms, sd 10 ms -> ~110 ms
    assert 180 <= f["pr_ms"] <= 230
    assert 380 <= f["qt_ms"] <= 450
    # QT grows with RR in the generator (Bazett scaling) and the delineator must see it
    assert beats.delineate(synth_beat(t, 1.2), 1.2)["qt_ms"] > beats.delineate(synth_beat(t, 0.6), 0.6)["qt_ms"] + 60


def test_pairing_and_blocks():
    bp = beats.pair_beats(make_synthetic(duration=90, hr=70, pat=0.25, seed=3))
    assert abs(np.median(bp.pat_ms) - 250) < 10
    rows, _ = beats.block_table(bp)
    assert len(rows) >= 5 and all(abs(r["rr_ms"] - r["pp_ms"]) < 15 for r in rows)


def test_ksg_and_te_known_values():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(2000)
    y = 0.9 * x + np.sqrt(1 - 0.81) * rng.standard_normal(2000)
    assert abs(infotheory.ksg_mi(x, y) - (-0.5 * np.log2(1 - 0.81))) < 0.1
    z = rng.standard_normal(3000)
    w = np.r_[0, 0.8 * z[:-1]] + 0.6 * rng.standard_normal(3000)
    assert infotheory.transfer_entropy(z, w) > 0.5 and infotheory.transfer_entropy(w, z) < 0.1


def test_agreement_identical_series():
    t = np.cumsum(np.full(400, 0.8))
    rr = 800 + 40 * np.sin(np.arange(400) / 5)
    rows = agreement.segment_agreement(t, rr, rr.copy(), np.full(400, 200.0), seg_s=120, min_s=60)
    assert rows and all(abs(r["rmssd_ecg"] - r["rmssd_ppg"]) < 1e-9 for r in rows)


def test_coherence_low_above_8hz():
    bp = beats.pair_beats(make_synthetic(duration=120, hr=72, seed=4))
    c, _ = coherence.record_coherence(bp)
    assert c["coh_0.5-3Hz"] > 0.5 and c["coh_15-40Hz"] < 0.2


def test_forward_identifiability_logic():
    fm = forward.ForwardModel()
    g = fm.crlb(th={"st_mm": 1.0}, n_beats=(100,), mode="tracking")
    assert np.isinf(g.set_index("param").loc["st_mm", "realistic_sd"])          # no mechanical link -> none
    g = fm.crlb(n_beats=(100,), mode="new_person").set_index("param")
    assert g.loc["hr", "detectable_realistic"]
    assert g.loc["qrs_ms", "realistic_sd"] > forward.CLINICAL_DELTA["qrs_ms"]    # timing only: unobservable
    sweep = forward.coupling_sweep("st_mm", [0.0, 0.1], "k_st")
    assert np.isinf(sweep.realistic_sd.iloc[0]) and np.isfinite(sweep.realistic_sd.iloc[1])


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
