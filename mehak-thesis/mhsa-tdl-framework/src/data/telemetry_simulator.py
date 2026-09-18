import numpy as np
import torch
from torch.utils.data import Dataset

METRIC_NAMES = ["cpu", "mem", "disk", "net"]

# Per-metric (L1, L2) thresholds, applied to the max value over the last
# 3 timesteps of a window (same "recent window" convention as the old
# ThresholdBaseline). Mirrors the None/L1/L2 banding used for SLA rules in
# Thapliyal (2026), "A Multi-Head Attention Approach for SLA Compliance
# Monitoring in Data Centers" (arXiv:2605.05354).
THRESHOLDS = {
    "cpu": (0.70, 0.85),
    "mem": (0.75, 0.90),
    "disk": (0.80, 0.90),
    "net": (0.75, 0.88),
}


class TelemetrySimulator:
    """Synthetic multivariate cluster telemetry (CPU, Mem, Disk, Net).

    This is a forecasting task, not same-window classification: the model
    only ever sees a `seq_length`-step *history* window. The label is
    computed from a separate `horizon`-step *future* window it never sees.
    A reactive threshold monitor (which only looks at the current/history
    window) has no way to observe the future window at all, so it can only
    "predict" a violation when the history window already shows one -- it
    structurally cannot get credit for foresight. This is what makes it a
    fair reproduction of the paper's "reactive vs. proactive" comparison.

    Two kinds of samples:
      - steady-state: gentle noise around a per-sample baseline load,
        never breaches a threshold.
      - transient: a fast multi-metric burst that starts somewhere around
        the history/future boundary. Bursts are correlated across metrics
        (e.g. a CPU spike drags Net up with it) -- a precursor that shows
        up in one metric's history can predict a different metric's
        future violation, which a strict one-head-per-metric model can't
        exploit but a cross-head fusion model can.
    """

    def __init__(self, num_samples=15000, seq_length=10, horizon=5, transient_ratio=0.3, seed=42):
        self.num_samples = num_samples
        self.seq_length = seq_length
        self.horizon = horizon
        self.total_length = seq_length + horizon
        self.num_features = 4
        self.transient_ratio = transient_ratio
        self.seed = seed

    def _label_future_window(self, future_segment):
        labels = np.zeros(self.num_features, dtype=np.int64)
        for i, name in enumerate(METRIC_NAMES):
            l1, l2 = THRESHOLDS[name]
            peak = future_segment[:, i].max()
            if peak >= l2:
                labels[i] = 2
            elif peak >= l1:
                labels[i] = 1
            else:
                labels[i] = 0
        return labels

    def generate_data(self):
        rng = np.random.RandomState(self.seed)

        baseline_load = rng.uniform(0.3, 0.5, size=(self.num_samples, 1, 1))
        X_full = baseline_load + rng.normal(
            loc=0.0, scale=0.06, size=(self.num_samples, self.total_length, self.num_features)
        )

        num_transient = int(self.num_samples * self.transient_ratio)
        transient_idx = rng.choice(self.num_samples, num_transient, replace=False)
        is_transient = np.zeros(self.num_samples, dtype=bool)

        # Correlated burst patterns: each pattern spikes 2-3 metrics together,
        # with one "primary" metric and one or two metrics that ride along.
        burst_patterns = [
            {"primary": 0, "riders": [3]},        # CPU spike drags Net up
            {"primary": 0, "riders": [2, 3]},     # CPU spike drags Disk+Net up
            {"primary": 1, "riders": [2]},        # Mem spike drags Disk up
            {"primary": 3, "riders": [0]},        # Net spike drags CPU up
        ]

        for idx in transient_idx:
            is_transient[idx] = True
            pattern = burst_patterns[rng.randint(len(burst_patterns))]
            ramp_len = rng.randint(3, 6)

            # The primary metric's own spike lands mostly/fully in the
            # future window (i.e. it shows little or no precursor of its
            # own in the visible history).
            primary_start = rng.randint(self.seq_length - 1, self.total_length - ramp_len + 1)
            ramp = np.linspace(0.0, 1.0, ramp_len) ** 1.5
            primary_gain = rng.uniform(0.5, 0.9)
            X_full[idx, primary_start:primary_start + ramp_len, pattern["primary"]] += ramp * primary_gain

            # Rider metrics lead the primary by a few steps -- a genuine
            # cross-metric precursor sitting inside the visible history
            # window, which is the only observable early-warning signal
            # for the primary's future violation.
            for rider in pattern["riders"]:
                lead_gap = rng.randint(3, 7)
                rider_start = max(primary_start - lead_gap, 0)
                rider_ramp_len = min(ramp_len, self.total_length - rider_start)
                rider_ramp = np.linspace(0.0, 1.0, rider_ramp_len) ** 1.5
                rider_gain = rng.uniform(0.35, 0.65) * primary_gain
                X_full[idx, rider_start:rider_start + rider_ramp_len, rider] += rider_ramp * rider_gain

        X_full = np.clip(X_full, 0.0, 1.0)

        X = X_full[:, :self.seq_length, :]                 # history window (model input)
        future = X_full[:, self.seq_length:, :]            # future window (never shown to the model)

        y = np.zeros((self.num_samples, self.num_features), dtype=np.int64)
        for idx in range(self.num_samples):
            y[idx] = self._label_future_window(future[idx])

        return X, y, is_transient


class TelemetryDataset(Dataset):
    def __init__(self, X, y, is_transient=None):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
        self.is_transient = (
            torch.BoolTensor(is_transient) if is_transient is not None
            else torch.zeros(len(X), dtype=torch.bool)
        )

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx], self.is_transient[idx]
