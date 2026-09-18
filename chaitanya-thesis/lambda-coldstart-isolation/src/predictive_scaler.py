# Resolves the gap in Wang et al. (2025) by implementing predictive provisioning 
# based on temporal access patterns rather than static warmth.
import math

class PredictiveAutoScaler:
    def __init__(self, history_len=1440):
        # 1440 minutes in a day
        self.history = [0] * history_len 
        self.warm_pool = 0

    def record_access(self, minute_of_day, invocations):
        self.history[minute_of_day] = invocations

    def scale_for_next_minute(self, current_minute):
        avg = sum(self.history) / len(self.history) if self.history else 0
        expected = self.history[(current_minute + 1) % len(self.history)]
        # Add dynamic buffer
        self.warm_pool = expected + math.ceil(avg * 0.1)
        return self.warm_pool
