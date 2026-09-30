"""Leakage, masking, scaling, physics and metric checks (run: pytest tests/ -q)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from masking import CHANNELS, FeatureBuilder, Imputer, make_keep, tabular, time_since_last  # noqa: E402
from models import BNN, RCPhysics, Recurrent, Scales, recurrent_loss  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data" / "processed" / "bldg59_hourly.csv"


def toy_frame(n=600, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2019-01-01", periods=n, freq="1h")
    df = pd.DataFrame(rng.normal(size=(n, len(CHANNELS))) + 20, index=idx, columns=CHANNELS)
    df["local_hour"], df["local_dow"], df["local_month"] = idx.hour, idx.dayofweek, idx.month
    return df


@pytest.mark.parametrize("pattern", ["mcar", "block"])
@pytest.mark.parametrize("rate", [0.1, 0.2, 0.3, 0.4])
def test_mask_rate_and_meter_untouched(pattern, rate):
    obs = np.ones((8000, len(CHANNELS)), bool)
    keep = make_keep(obs, pattern, rate, seed=3)
    lost = 1 - keep[:, :8].mean()
    assert abs(lost - rate) < 0.05
    assert keep[:, 8].all()


def test_masks_are_reproducible_and_seed_dependent():
    obs = np.ones((2000, 9), bool)
    a, b, c = (make_keep(obs, "block", 0.2, s) for s in (1, 1, 2))
    assert (a == b).all() and (a != c).any()


def test_block_outages_are_contiguous():
    obs = np.ones((5000, 9), bool)
    keep = make_keep(obs, "block", 0.2, 0)
    col = ~keep[:, 0]
    runs = np.diff(np.flatnonzero(np.diff(np.r_[0, col.astype(int), 0])))[::2]
    assert runs.min() >= 6


def test_natural_gaps_never_reappear():
    obs = np.random.default_rng(0).random((3000, 9)) > 0.1
    for pattern in ("mcar", "block"):
        assert not (make_keep(obs, pattern, 0.3, 0) & ~obs).any()


def test_features_are_causal():
    """Changing the future must not change features at or before hour h."""
    df = toy_frame()
    fb = FeatureBuilder(df, np.arange(len(df)) < 400)
    keep = make_keep(fb.observed, "mcar", 0.3, 0)
    f1, imp1 = fb.frame(keep)
    fb.values[451:] += 100.0
    f2, imp2 = fb.frame(keep)
    assert np.allclose(f1[:451], f2[:451])
    rows = np.arange(200, 451)
    assert np.allclose(tabular(f1, imp1, rows, 0, 1), tabular(f2, imp2, rows, 0, 1))


def test_scaling_uses_training_rows_only():
    df = toy_frame()
    train = np.arange(len(df)) < 300
    fb1 = FeatureBuilder(df, train)
    df2 = df.copy()
    df2.iloc[300:, :9] += 50
    fb2 = FeatureBuilder(df2, train)
    assert np.allclose(fb1.mu, fb2.mu) and np.allclose(fb1.sd, fb2.sd)


def test_locf_and_time_since_last():
    v = np.array([[1.0], [2.0], [3.0], [4.0]])
    keep = np.array([[True], [False], [False], [True]])
    imp = Imputer("locf", v, np.ones(4, bool))(v, keep)
    assert imp[:, 0].tolist() == [1.0, 1.0, 1.0, 4.0]
    assert time_since_last(keep)[:, 0].tolist() == [0, 1, 2, 0]


def test_inverse_scaling_round_trip():
    sc = Scales(40.0, 20.0, 23.0, 0.8, 0.3)
    y = torch.tensor([10.0, 40.0, 90.0])
    z = (y - sc.mu_e) / sc.sd_e
    assert torch.allclose(z * sc.sd_e + sc.mu_e, y)


def test_physics_loss_zero_for_consistent_targets():
    torch.manual_seed(0)
    m = Recurrent(34, dual=True, physics=True).eval()
    sc = Scales(0.0, 1.0, 0.0, 1.0, 1.0)
    x = torch.randn(16, 24, 34)
    drv = torch.randn(16, 4)
    with torch.no_grad():
        pe, pt = m(x)
        a, b, c, d, e = m.physics.coefs()
        tnow = (pt - a * drv[:, 0] - b * drv[:, 3] * pe - c * drv[:, 1] - d * drv[:, 2] - e) / (1 - a)
    for w in (torch.ones(16), torch.zeros(16)):
        batch = (x, pe, pt, tnow, drv, w)
        assert torch.isclose(recurrent_loss(m, batch, sc, lam=1.0), recurrent_loss(m, batch, sc, lam=0.0), atol=1e-4)
    assert all(float(c) > 0 for c in RCPhysics().coefs()[:4])


def test_metrics():
    import importlib
    exp = importlib.import_module("experiment")
    y = np.array([1.0, 2.0, 3.0, 4.0])
    m = exp.metrics(y, y + 1)
    assert m["MAE"] == 1 and m["RMSE"] == 1 and m["neg_pct"] == 0
    assert np.isclose(exp.metrics(y, y)["R2"], 1.0)
    assert np.isclose(exp.metrics(np.array([0.5, 2.0]), np.array([0.0, 3.0]))["MAPE"], 0.5)


def test_bnn_kl_positive_and_shapes():
    b = BNN(12)
    mu, s = b(torch.randn(5, 12))
    assert mu.shape == (5,) and (s > 0).all() and float(b.kl()) > 0


@pytest.mark.skipif(not DATA.exists(), reason="run src/prepare_data.py first")
def test_split_is_chronological_and_disjoint():
    import importlib
    exp = importlib.import_module("experiment")
    d = exp.Data()
    order = [d.time[d.rows[k]] for k in ("train", "val", "test")]
    for a, b in zip(order, order[1:]):
        assert a.max() < b.min()
    for k in d.rows:  # the target hour h+1 always lies in the same period as h
        assert np.isfinite(d.ye[d.rows[k]]).all()
