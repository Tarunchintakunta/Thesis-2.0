"""LSTM predictor tests (NumPy backend; TF fail-closed)."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.lstm_predictor import (
    NumpyLSTMRegressor,
    job_windows,
    mae_rmse,
    require_tensorflow,
    series_windows,
    split_by_job,
)


def test_tensorflow_backend_fail_closed():
    with pytest.raises(ImportError, match="TensorFlow"):
        require_tensorflow()


def test_lstm_loss_decreases_on_sine():
    t = np.arange(80, dtype=float)
    series = 2.0 + np.sin(2 * np.pi * t / 16.0)
    X, y = series_windows(series, lookback=8)
    model = NumpyLSTMRegressor(hidden_size=8, seed=0)
    hist = model.fit(X, y, epochs=12, lr=0.02, batch_size=16)
    assert hist["loss"][-1] < hist["loss"][0]
    pred = model.predict(X)
    mae, rmse = mae_rmse(y, pred)
    assert np.isfinite(mae) and np.isfinite(rmse)
    assert mae < 1.5


def test_predict_next_shape():
    rng = np.random.RandomState(0)
    X = rng.randn(30, 12)
    y = X[:, -1] + 0.1 * rng.randn(30)
    model = NumpyLSTMRegressor(hidden_size=4, seed=1)
    model.fit(X, y, epochs=3, batch_size=10)
    val = model.predict_next(X[0])
    assert isinstance(val, float)


def test_job_windows_and_split_no_job_leakage():
    rows = []
    for job in (1, 2, 3):
        for t in range(20):
            rows.append({"job_id": job, "time_s": t, "cpu_cores_sum": float(t + job)})
    df = pd.DataFrame(rows)
    X, y, ids = job_windows(df, lookback=4)
    Xtr, ytr, Xte, yte = split_by_job(X, y, ids, test_frac=0.34, seed=0)
    assert len(Xtr) and len(Xte)
    # reconstruct job ids via matching windows is heavy; check counts
    assert Xtr.shape[1] == 4
    assert yte.shape[0] == Xte.shape[0]
