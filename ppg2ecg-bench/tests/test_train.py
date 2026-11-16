"""Tests for the authors'-recipe training plumbing that do not need torch or the authors' repos."""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.datasets import make_synthetic  # noqa: E402
from bench.models.trained import ClepGAN, P2EWGAN  # noqa: E402
from bench.train import common, p2e  # noqa: E402


def test_budget_runner_stops_scripts_without_newlines_and_has_np_long():
    d = Path(tempfile.mkdtemp())
    (d / "s.py").write_text("import numpy as np, sys, time\nx = np.long(3)\n"
                            "for i in range(10**6):\n    sys.stdout.write('\\r%d' % i); sys.stdout.flush(); time.sleep(0.01)\n")
    status, secs = common.run_budgeted([sys.executable, str(d / "s.py")], str(d), 3, d / "log.txt",
                                       env=common.compat_env(d))
    assert status == "timeout" and secs < 20 and (d / "log.txt").stat().st_size > 0


def test_detect_norm():
    rng = np.random.default_rng(0)
    w = rng.standard_normal((50, 300))
    assert common.detect_norm(w) == "zscore_window"
    mm = 2 * (w - w.min(1, keepdims=True)) / np.ptp(w, axis=1, keepdims=True) - 1
    assert common.detect_norm(mm) == "minmax_window"


def test_budget_loader_cuts_epochs_to_one_batch():
    import time
    bl = common.BudgetLoader(list(range(10)), deadline=time.time() - 1)
    assert list(bl) == [0] and list(bl) == [0] and bl.exhausted_at_epoch == 1


def test_p2e_fallback_layout():
    recs = [make_synthetic(subject=f"s{i}", duration=60, fs=125, seed=i) for i in range(5)]
    d, test = p2e._build_from_cache(recs, Path(tempfile.mkdtemp()))
    for f in p2e.FILES:
        a = np.load(d / f)
        assert a.shape[1] == 375 and a.dtype == np.float32
    assert len(test) == 1


def test_trained_adapter_inputs_match_training_format():
    d = Path(tempfile.mkdtemp())
    (d / "meta.json").write_text(json.dumps(dict(fs=125.0, window=512, segment=128, filter_size=[64] * 6,
                                                 kernel_size=[31] * 6, trained_on={"bidmc": "possibly"})))
    ad = ClepGAN(str(d))
    w = ad.normalize_window(np.random.default_rng(1).standard_normal((2, 512)))
    seg = w.reshape(2, 4, 128)
    assert ad.window_len == 512 and np.allclose(seg.max(-1), 1) and np.allclose(seg.min(-1), -1)
    (d / "meta.json").write_text(json.dumps(dict(fs=125.0, window=375, ppg_stats={"norm": "zscore_window"})))
    w = P2EWGAN(str(d)).normalize_window(np.random.default_rng(2).standard_normal((2, 375)) * 5 + 3)
    assert np.allclose(w.mean(1), 0, atol=1e-9)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
