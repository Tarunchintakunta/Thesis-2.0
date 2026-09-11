"""D1a - One-class SVM (Schölkopf et al., 2001) on the count view.

Trained on clean windows only. The alarm threshold is the configured quantile
of the model's own scores on its training windows, so no label is ever used.
"""
from __future__ import annotations

import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM


class OcsvmDetector:
    name = "d1_ocsvm"

    def __init__(self, kernel: str = "rbf", gamma: str | float = "scale", nu: float = 0.05,
                 threshold_quantile: float = 0.99) -> None:
        self.params = {"kernel": kernel, "gamma": gamma, "nu": nu}
        self.threshold_quantile = threshold_quantile
        self.model = None
        self.threshold = np.inf

    def fit(self, X: np.ndarray) -> "OcsvmDetector":
        self.model = make_pipeline(StandardScaler(), OneClassSVM(**self.params)).fit(X)
        self.threshold = float(np.quantile(self.score(X), self.threshold_quantile))
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        # decision_function > 0 means "inside" -> flip so higher = more anomalous
        return -self.model.decision_function(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.score(X) > self.threshold
