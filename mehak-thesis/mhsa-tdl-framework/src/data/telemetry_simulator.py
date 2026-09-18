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

    Two kinds of samples:
      - steady-state: gentle noise around a per-sample baseline load.
      - transient: a fast multi-metric burst injected into the last few
        timesteps. Bursts are correlated across metrics (e.g. a CPU spike
        tends to drag Net/Disk up with it), which is what a strict
        one-head-per-metric model cannot exploit but a cross-head fusion
        model can.
    """

    def __init__(self, num_samples=15000, seq_length=10, transient_ratio=0.3, seed=42):
        self.num_samples = num_samples
        self.seq_length = seq_length
        self.num_features = 4
        self.transient_ratio = transient_ratio
        self.seed = seed

    def _label_window(self, sample):
        recent = sample[-3:]
        labels = np.zeros(self.num_features, dtype=np.int64)
        for i, name in enumerate(METRIC_NAMES):
            l1, l2 = THRESHOLDS[name]
            peak = recent[:, i].max()
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
        X = baseline_load + rng.normal(loc=0.0, scale=0.06, size=(self.num_samples, self.seq_length, self.num_features))

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
            ramp_len = rng.randint(3, 5)
            ramp = np.linspace(0.0, 1.0, ramp_len) ** 1.5  # fast, non-linear ramp-up

            primary_gain = rng.uniform(0.45, 0.85)
            X[idx, -ramp_len:, pattern["primary"]] += ramp * primary_gain

            for rider in pattern["riders"]:
                rider_gain = rng.uniform(0.2, 0.5) * primary_gain
                X[idx, -ramp_len:, rider] += ramp * rider_gain

        X = np.clip(X, 0.0, 1.0)

        y = np.zeros((self.num_samples, self.num_features), dtype=np.int64)
        for idx in range(self.num_samples):
            y[idx] = self._label_window(X[idx])

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
