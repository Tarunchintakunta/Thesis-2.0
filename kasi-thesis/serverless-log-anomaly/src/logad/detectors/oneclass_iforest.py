"""D1b - Isolation Forest (Liu, Ting and Zhou, 2008) on the count view.

Same protocol as the OC-SVM: clean windows only, threshold = quantile of the
training scores.
"""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


class IforestDetector:
    name = "d1_iforest"

    def __init__(self, n_estimators: int = 200, max_samples="auto", random_state: int = 0,
                 threshold_quantile: float = 0.99) -> None:
        self.params = {"n_estimators": n_estimators, "max_samples": max_samples, "random_state": random_state}
        self.threshold_quantile = threshold_quantile
        self.model = None
        self.threshold = np.inf

    def fit(self, X: np.ndarray) -> "IforestDetector":
        self.model = make_pipeline(StandardScaler(), IsolationForest(**self.params)).fit(X)
        self.threshold = float(np.quantile(self.score(X), self.threshold_quantile))
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        # score_samples is higher for normal points -> flip it
        return -self.model.score_samples(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.score(X) > self.threshold
