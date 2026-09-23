"""Classical monitors named in.

Trained on flattened history windows from the *same* feature matrix as MHSA.
These are scaffold baselines for metric-suite completeness on whatever dataset
the caller provides. — synthetic scores are not formal evidence."""

from __future__ import annotations

import time
from typing import Dict, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler


def _flatten(X: np.ndarray) -> np.ndarray:
    # (N, T, M) -> (N, T*M)
    return X.reshape(X.shape[0], -1)


def _fit_predict_multimetric(
    estimator_factory,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, float]:
    """Fit one classifier per metric; return preds, decision/prob scores, latency_ms."""
    Xtr = _flatten(X_train)
    Xte = _flatten(X_test)
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(Xtr)
    Xte = scaler.transform(Xte)

    n_metrics = y_train.shape[1]
    preds = np.zeros((X_test.shape[0], n_metrics), dtype=np.int64)
    # score matrix for ROC-AUC: (N, metrics, 3) — use predict_proba when available
    scores = np.zeros((X_test.shape[0], n_metrics, 3), dtype=np.float64)

    t0 = time.time()
    for m in range(n_metrics):
        clf = estimator_factory()
        clf.fit(Xtr, y_train[:, m])
        preds[:, m] = clf.predict(Xte)
        if hasattr(clf, "predict_proba"):
            proba = clf.predict_proba(Xte)
            # align columns to classes 0,1,2
            full = np.zeros((X_test.shape[0], 3), dtype=np.float64)
            for i, c in enumerate(clf.classes_):
                full[:, int(c)] = proba[:, i]
            scores[:, m, :] = full
        elif hasattr(clf, "decision_function"):
            dec = clf.decision_function(Xte)
            if dec.ndim == 1:
                # binary edge case
                full = np.zeros((X_test.shape[0], 3), dtype=np.float64)
                full[:, 1] = dec
                scores[:, m, :] = full
            else:
                full = np.zeros((X_test.shape[0], 3), dtype=np.float64)
                for i, c in enumerate(clf.classes_):
                    full[:, int(c)] = dec[:, i]
                scores[:, m, :] = full
        else:
            # one-hot fallback from hard preds
            scores[np.arange(X_test.shape[0]), m, preds[:, m]] = 1.0
    latency_ms = (time.time() - t0) * 1000 / max(len(X_test), 1)
    return preds, scores, latency_ms


def run_classical_baselines(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
) -> Dict[str, Tuple[np.ndarray, np.ndarray, float]]:
    """Return name -> (preds, score_tensor, latency_ms)."""
    factories = {
        "RF (classical)": lambda: RandomForestClassifier(
            n_estimators=100, max_depth=12, random_state=0, n_jobs=-1
        ),
        "KNN (classical)": lambda: KNeighborsClassifier(n_neighbors=15),
        "SVM (classical)": lambda: LinearSVC(max_iter=2000, dual=False),
    }
    out = {}
    for name, factory in factories.items():
        out[name] = _fit_predict_multimetric(factory, X_train, y_train, X_test)
    return out
