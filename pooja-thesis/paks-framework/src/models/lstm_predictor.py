"""Vanilla LSTM workload predictor (formal PAKS path).

TensorFlow is named in the  resources table. On this CPython 3.14 host there
is no TF wheel; ``require_tensorflow()`` fails closed. Default trainer is a
NumPy LSTM cell with BPTT (architecture = LSTM, runtime = numpy)."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

LOOKBACK = 12
HIDDEN = 16


def require_tensorflow():
    """Fail closed: do not silently fall back to MLP when TF is requested."""
    try:
        import tensorflow as tf  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "TensorFlow backend requested but not importable (typical on CPython "
            "runnable LSTM is NumPy BPTT. See pooja-thesis/DATA_GAPS.md."
        ) from exc
    import tensorflow as tf

    return tf


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20.0, 20.0)))


def job_windows(
    jobs: pd.DataFrame,
    lookback: int = LOOKBACK,
    min_std: float = 1e-6,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build (X, y, job_id) windows. No cross-job padding or imputed gaps."""
    xs, ys, ids = [], [], []
    for job_id, g in jobs.groupby("job_id"):
        g = g.sort_values("time_s")
        v = g["cpu_cores_sum"].to_numpy(dtype=np.float64)
        if v.size <= lookback or float(np.std(v)) < min_std:
            continue
        for i in range(v.size - lookback):
            xs.append(v[i : i + lookback])
            ys.append(v[i + lookback])
            ids.append(job_id)
    if not xs:
        raise ValueError("no LSTM windows (need jobs with > lookback bins and non-zero variance)")
    return np.asarray(xs, dtype=np.float64), np.asarray(ys, dtype=np.float64), np.asarray(ids)


def series_windows(series: np.ndarray, lookback: int = LOOKBACK) -> Tuple[np.ndarray, np.ndarray]:
    v = np.asarray(series, dtype=np.float64)
    if v.size <= lookback:
        raise ValueError(f"series length {v.size} <= lookback {lookback}")
    X = np.stack([v[i : i + lookback] for i in range(v.size - lookback)])
    y = v[lookback:]
    return X, y


def split_by_job(
    X: np.ndarray,
    y: np.ndarray,
    job_ids: np.ndarray,
    test_frac: float = 0.2,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    uniq = np.unique(job_ids)
    rng.shuffle(uniq)
    n_test = max(1, int(round(test_frac * uniq.size)))
    test_jobs = set(uniq[:n_test].tolist())
    test_mask = np.array([j in test_jobs for j in job_ids])
    if not test_mask.any() or test_mask.all():
        n = X.shape[0]
        cut = max(1, int(round(test_frac * n)))
        return X[cut:], y[cut:], X[:cut], y[:cut]
    return X[~test_mask], y[~test_mask], X[test_mask], y[test_mask]


class NumpyLSTMRegressor:
    """Single-layer LSTM → linear head. Input is a lookback vector (univariate)."""

    def __init__(self, hidden_size: int = HIDDEN, seed: int = 42):
        self.hidden_size = int(hidden_size)
        self.seed = int(seed)
        self.input_size = 1
        self.mean_ = 0.0
        self.std_ = 1.0
        self.backend = "numpy-lstm"
        self._init_weights()

    def _init_weights(self) -> None:
        rng = np.random.RandomState(self.seed)
        h = self.hidden_size
        d = self.input_size + h
        scale = 1.0 / np.sqrt(d)
        self.W = rng.randn(d, 4 * h) * scale
        self.b = np.zeros(4 * h)
        self.b[:h] = 1.0  # forget-gate bias
        self.Wy = rng.randn(h) * (1.0 / np.sqrt(h))
        self.by = 0.0

    def _forward_batch(self, X: np.ndarray):
        """X: (B, T) un-normalized or normalized. Returns yhat (B,), cache."""
        B, T = X.shape
        h = self.hidden_size
        hs = np.zeros((T + 1, B, h))
        cs = np.zeros((T + 1, B, h))
        xs = np.zeros((T, B, self.input_size + h))
        gates = np.zeros((T, B, 4 * h))
        i_s = np.zeros((T, B, h))
        f_s = np.zeros((T, B, h))
        o_s = np.zeros((T, B, h))
        g_s = np.zeros((T, B, h))
        for t in range(T):
            xt = X[:, t : t + 1]
            xh = np.concatenate([xt, hs[t]], axis=1)
            z = xh @ self.W + self.b
            ig = sigmoid(z[:, :h])
            fg = sigmoid(z[:, h : 2 * h])
            og = sigmoid(z[:, 2 * h : 3 * h])
            gg = np.tanh(z[:, 3 * h :])
            c = fg * cs[t] + ig * gg
            ht = og * np.tanh(c)
            xs[t] = xh
            gates[t] = z
            i_s[t], f_s[t], o_s[t], g_s[t] = ig, fg, og, gg
            cs[t + 1] = c
            hs[t + 1] = ht
        yhat = hs[-1] @ self.Wy + self.by
        cache = (xs, gates, i_s, f_s, o_s, g_s, cs, hs, X)
        return yhat, cache

    def _backward_batch(self, yhat: np.ndarray, y: np.ndarray, cache):
        xs, gates, i_s, f_s, o_s, g_s, cs, hs, X = cache
        B, T = X.shape
        h = self.hidden_size
        dy = (2.0 / B) * (yhat - y)
        dWy = hs[-1].T @ dy
        dby = float(np.sum(dy))
        dW = np.zeros_like(self.W)
        db = np.zeros_like(self.b)
        dh_next = np.outer(dy, self.Wy)
        dc_next = np.zeros((B, h))
        for t in range(T - 1, -1, -1):
            c = cs[t + 1]
            c_prev = cs[t]
            tanh_c = np.tanh(c)
            og, ig, fg, gg = o_s[t], i_s[t], f_s[t], g_s[t]
            dh = dh_next
            do = dh * tanh_c
            dc = dh * og * (1.0 - tanh_c ** 2) + dc_next
            di = dc * gg
            dg = dc * ig
            df = dc * c_prev
            dc_prev = dc * fg
            dz_i = di * ig * (1.0 - ig)
            dz_f = df * fg * (1.0 - fg)
            dz_o = do * og * (1.0 - og)
            dz_g = dg * (1.0 - gg ** 2)
            dz = np.concatenate([dz_i, dz_f, dz_o, dz_g], axis=1)
            xh = xs[t]
            dW += xh.T @ dz
            db += dz.sum(axis=0)
            dxh = dz @ self.W.T
            dh_next = dxh[:, self.input_size :]
            dc_next = dc_prev
        # clip
        for arr in (dW, db, dWy):
            np.clip(arr, -5.0, 5.0, out=arr)
        dby = float(np.clip(dby, -5.0, 5.0))
        return dW, db, dWy, dby

    def _normalize(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mean_) / self.std_

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 12,
        lr: float = 8e-3,
        batch_size: int = 64,
        verbose: bool = False,
    ) -> Dict[str, list]:
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        self.mean_ = float(np.mean(X))
        self.std_ = float(np.std(X) + 1e-8)
        Xn = self._normalize(X)
        yn = (y - self.mean_) / self.std_
        n = Xn.shape[0]
        rng = np.random.RandomState(self.seed + 7)
        # Adam
        mW = np.zeros_like(self.W)
        vW = np.zeros_like(self.W)
        mb = np.zeros_like(self.b)
        vb = np.zeros_like(self.b)
        mWy = np.zeros_like(self.Wy)
        vWy = np.zeros_like(self.Wy)
        mby = 0.0
        vby = 0.0
        b1, b2, eps = 0.9, 0.999, 1e-8
        step = 0
        history = {"loss": []}
        for epoch in range(epochs):
            perm = rng.permutation(n)
            losses = []
            for start in range(0, n, batch_size):
                idx = perm[start : start + batch_size]
                xb, yb = Xn[idx], yn[idx]
                yhat, cache = self._forward_batch(xb)
                losses.append(float(np.mean((yhat - yb) ** 2)))
                dW, db, dWy, dby = self._backward_batch(yhat, yb, cache)
                step += 1
                for p, g, m, v, name in (
                    (self.W, dW, mW, vW, "W"),
                    (self.b, db, mb, vb, "b"),
                    (self.Wy, dWy, mWy, vWy, "Wy"),
                ):
                    m *= b1
                    m += (1 - b1) * g
                    v *= b2
                    v += (1 - b2) * (g ** 2)
                    mhat = m / (1 - b1 ** step)
                    vhat = v / (1 - b2 ** step)
                    p -= lr * mhat / (np.sqrt(vhat) + eps)
                mby = b1 * mby + (1 - b1) * dby
                vby = b2 * vby + (1 - b2) * (dby ** 2)
                self.by -= lr * (mby / (1 - b1 ** step)) / (np.sqrt(vby / (1 - b2 ** step)) + eps)
            history["loss"].append(float(np.mean(losses)))
            if verbose:
                print(f"epoch {epoch+1}/{epochs} mse={history['loss'][-1]:.6f}")
        return history

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        yhat_n = self._forward_batch(self._normalize(X))[0]
        return yhat_n * self.std_ + self.mean_

    def predict_next(self, window: np.ndarray) -> float:
        return float(self.predict(np.asarray(window, dtype=np.float64).reshape(1, -1))[0])


def mae_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, float]:
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    err = y_true - y_pred
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    return mae, rmse


def train_lstm_on_jobs(
    jobs: pd.DataFrame,
    lookback: int = LOOKBACK,
    hidden_size: int = HIDDEN,
    seed: int = 42,
    max_train_windows: int = 4000,
    epochs: int = 10,
    backend: str = "numpy-lstm",
) -> Tuple[NumpyLSTMRegressor, Dict[str, float]]:
    if backend == "tensorflow":
        require_tensorflow()
    X, y, ids = job_windows(jobs, lookback=lookback)
    Xtr, ytr, Xte, yte = split_by_job(X, y, ids, seed=seed)
    rng = np.random.RandomState(seed)
    if Xtr.shape[0] > max_train_windows:
        pick = rng.choice(Xtr.shape[0], size=max_train_windows, replace=False)
        Xtr, ytr = Xtr[pick], ytr[pick]
    model = NumpyLSTMRegressor(hidden_size=hidden_size, seed=seed)
    model.fit(Xtr, ytr, epochs=epochs)
    pred_tr = model.predict(Xtr)
    pred_te = model.predict(Xte)
    mae_tr, rmse_tr = mae_rmse(ytr, pred_tr)
    mae_te, rmse_te = mae_rmse(yte, pred_te)
    persist = Xte[:, -1]
    mae_p, rmse_p = mae_rmse(yte, persist)
    metrics = {
        "n_train_windows": int(Xtr.shape[0]),
        "n_test_windows": int(Xte.shape[0]),
        "lookback": int(lookback),
        "hidden_size": int(hidden_size),
        "backend": model.backend,
        "mae_train": mae_tr,
        "rmse_train": rmse_tr,
        "mae_test": mae_te,
        "rmse_test": rmse_te,
        "mae_persistence_test": mae_p,
        "rmse_persistence_test": rmse_p,
        "evidence": "TRACE",
        "split": "held-out jobs (no window leakage)",
    }
    return model, metrics
