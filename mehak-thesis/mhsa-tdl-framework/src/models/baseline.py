import numpy as np

from src.data.telemetry_simulator import METRIC_NAMES, THRESHOLDS


class ThresholdBaseline:
    """Traditional reactive monitoring: flags a violation only once a metric
    has already crossed its threshold in the observed window. Per-metric
    None/L1/L2 output, so it's directly comparable to the attention models."""

    def predict(self, X):
        """X: (num_samples, seq_length, num_metrics) -> (num_samples, num_metrics) int labels"""
        recent = X[:, -3:, :]
        peak = recent.max(axis=1)  # (num_samples, num_metrics)

        labels = np.zeros((X.shape[0], X.shape[2]), dtype=np.int64)
        for i, name in enumerate(METRIC_NAMES):
            l1, l2 = THRESHOLDS[name]
            labels[:, i] = np.where(peak[:, i] >= l2, 2, np.where(peak[:, i] >= l1, 1, 0))
        return labels
