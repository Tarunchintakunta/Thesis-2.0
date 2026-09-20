"""Aldomi SelectKBest + GRU + RF pipeline on tiny tensors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.models.aldomi_hybrid import run_aldomi_hybrid


def test_aldomi_hybrid_shapes_and_selectk():
    rng = np.random.RandomState(0)
    n, t, f = 80, 10, 13
    X = rng.rand(n, t, f).astype(np.float32)
    # Make channel 0 informative for the max-label.
    y = np.zeros((n, 4), dtype=np.int64)
    y[:, 0] = (X[:, :, 0].mean(axis=1) > 0.5).astype(np.int64)
    y[:, 1] = y[:, 0]
    X_train, y_train = X[:60], y[:60]
    X_test, y_test = X[60:], y[60:]
    out = run_aldomi_hybrid(
        X_train, y_train, X_test, k=6, seed=0, epochs=2, hidden=8, heads=["Aldomi GRU-RF"]
    )
    assert "Aldomi GRU-RF" in out
    preds, scores, lat, info = out["Aldomi GRU-RF"]
    assert preds.shape == (20, 4)
    assert scores.shape == (20, 4, 3)
    assert lat >= 0
    assert info["k_used"] <= 6
    assert info["clone"] is False
    assert info["net_channel_is_network_bytes"] is False
    assert set(np.unique(preds)).issubset({0, 1, 2})
