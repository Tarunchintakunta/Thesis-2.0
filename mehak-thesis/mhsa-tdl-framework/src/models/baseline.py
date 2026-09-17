import numpy as np

class ThresholdBaseline:
    def __init__(self, cpu_threshold=0.85, mem_threshold=0.90, disk_threshold=0.90):
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.disk_threshold = disk_threshold

    def predict(self, X):
        """
        X: numpy array of shape (num_samples, seq_length, num_features)
        Returns: binary predictions (1 if threshold exceeded in any of the last few timesteps)
        """
        predictions = []
        for sample in X:
            # Check the last 3 timesteps for any threshold violation
            recent_steps = sample[-3:]
            cpu_violation = np.any(recent_steps[:, 0] > self.cpu_threshold)
            mem_violation = np.any(recent_steps[:, 1] > self.mem_threshold)
            disk_violation = np.any(recent_steps[:, 2] > self.disk_threshold)

            if cpu_violation or mem_violation or disk_violation:
                predictions.append(1)
            else:
                predictions.append(0)

        return np.array(predictions)
