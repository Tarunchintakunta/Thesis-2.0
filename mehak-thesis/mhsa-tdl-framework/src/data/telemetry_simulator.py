import numpy as np
import torch
from torch.utils.data import Dataset

class TelemetrySimulator:
    def __init__(self, num_samples=10000, seq_length=10):
        self.num_samples = num_samples
        self.seq_length = seq_length
        self.num_features = 4 # CPU, Mem, Disk, Net

    def generate_data(self):
        # Generate synthetic normal data
        np.random.seed(42)
        X = np.random.normal(loc=0.5, scale=0.1, size=(self.num_samples, self.seq_length, self.num_features))
        y = np.zeros(self.num_samples)

        # Inject failures (anomalies) in about 15% of the samples
        num_anomalies = int(self.num_samples * 0.15)
        anomaly_indices = np.random.choice(self.num_samples, num_anomalies, replace=False)

        for idx in anomaly_indices:
            # Anomalies: sudden spikes in CPU and memory or Disk
            spike_type = np.random.choice([0, 1, 2])
            if spike_type == 0:
                X[idx, -3:, 0] += np.random.uniform(0.4, 0.8) # CPU spike
            elif spike_type == 1:
                X[idx, -3:, 1] += np.random.uniform(0.5, 0.9) # Mem spike
            else:
                X[idx, -3:, 2] += np.random.uniform(0.6, 1.0) # Disk spike

            y[idx] = 1.0 # 1 indicates failure/anomaly

        # Clip values to realistic ranges [0, 1]
        X = np.clip(X, 0, 1)

        return X, y

class TelemetryDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
