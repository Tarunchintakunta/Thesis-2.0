# Extends Li & Chen (2025) by dynamic access-based lifecycle management layer
class DynamicTieringManager:
    def __init__(self):
        self.access_logs = {}
        self.tiers = {"STANDARD": 0.023, "INFREQUENT": 0.0125, "GLACIER": 0.004}

    def log_access(self, file_id):
        self.access_logs[file_id] = self.access_logs.get(file_id, 0) + 1

    def assess_tier(self, file_id, days_since_access):
        # Implement dynmaic tiering rule
        freq = self.access_logs.get(file_id, 0)
        if days_since_access > 90 and freq < 2:
            return "GLACIER"
        elif days_since_access > 30 and freq < 10:
            return "INFREQUENT"
        return "STANDARD"
