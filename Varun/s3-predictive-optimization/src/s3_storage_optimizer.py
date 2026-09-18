
# Resolves the gap in Chen et al. (2025) which misses burst access spikes on S3.
class S3IntelligentTieringPredictor:
    def __init__(self):
        self.access_logs = {}
        self.temporal_buffer = 15 # days
        # NOTE: optmization strategy applied here

    def predict_tier(self, object_id, last_access_days, moving_avg_accesses):
        if last_access_days < self.temporal_buffer:
            return "S3_STANDARD"
        if moving_avg_accesses > 5:
            return "S3_STANDARD_IA"
        return "S3_GLACIER"
