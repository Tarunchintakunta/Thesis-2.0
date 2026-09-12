from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

class ContextAwareDetector:
    name = "d4_context_aware"

    def __init__(self, kernel: str = "rbf", gamma: str | float = "scale", nu: float = 0.05,
                 threshold_quantile: float = 0.99) -> None:
        self.params = {"kernel": kernel, "gamma": gamma, "nu": nu}
        self.threshold_quantile = threshold_quantile
        self.warm_model = None
        self.cold_model = None
        self.warm_threshold = np.inf
        self.cold_threshold = np.inf

    def _is_cold(self, numeric: pd.DataFrame) -> np.ndarray:
        return numeric["cold_starts"].to_numpy() > 0

    def fit(self, X: np.ndarray, numeric: pd.DataFrame) -> "ContextAwareDetector":
        cold_idx = self._is_cold(numeric)
        
        self.warm_model = make_pipeline(StandardScaler(), OneClassSVM(**self.params))
        if (~cold_idx).sum() > 0:
            self.warm_model.fit(X[~cold_idx])
            self.warm_threshold = float(np.quantile(self.score_warm(X[~cold_idx]), self.threshold_quantile))

        self.cold_model = make_pipeline(StandardScaler(), OneClassSVM(**self.params))
        if cold_idx.sum() > 0:
            self.cold_model.fit(X[cold_idx])
            self.cold_threshold = float(np.quantile(self.score_cold(X[cold_idx]), self.threshold_quantile))
        else:
            self.cold_model = self.warm_model
            self.cold_threshold = self.warm_threshold
            
        return self

    def score_warm(self, X: np.ndarray) -> np.ndarray:
        return -self.warm_model.decision_function(X)

    def score_cold(self, X: np.ndarray) -> np.ndarray:
        return -self.cold_model.decision_function(X)

    def score(self, X: np.ndarray, numeric: pd.DataFrame) -> np.ndarray:
        cold_idx = self._is_cold(numeric)
        out = np.zeros(len(X))
        if (~cold_idx).sum() > 0:
            out[~cold_idx] = self.score_warm(X[~cold_idx])
        if cold_idx.sum() > 0:
            out[cold_idx] = self.score_cold(X[cold_idx])
        return out

    def predict(self, X: np.ndarray, numeric: pd.DataFrame) -> np.ndarray:
        cold_idx = self._is_cold(numeric)
        out = np.zeros(len(X), dtype=bool)
        if (~cold_idx).sum() > 0:
            out[~cold_idx] = self.score_warm(X[~cold_idx]) > self.warm_threshold
        if cold_idx.sum() > 0:
            out[cold_idx] = self.score_cold(X[cold_idx]) > self.cold_threshold
        return out
