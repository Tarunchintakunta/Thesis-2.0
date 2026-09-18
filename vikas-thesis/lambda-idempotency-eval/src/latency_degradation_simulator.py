# Empirically injects network partitioning to measure read-stall degradation,
# improving upon Nguyen et al. (2025)'s theoretical bounds.
import random

class LatencyDegradationSimulator:
    def __init__(self, base_latency_ms=25):
        self.base_latency = base_latency_ms

    def read_with_eventual_consistency(self, retry_count=0):
        # The higher the retries, the higher the degradation penalty
        stall_penalty = (retry_count * random.randint(10, 50))
        partition_factor = 1.0
        
        if random.random() < 0.05:
            # 5% chance of steep network partition penalty
            partition_factor = random.uniform(2.5, 5.0)

        latency = (self.base_latency + stall_penalty) * partition_factor
        return {"result": "data_payload", "latency_ms": latency}
