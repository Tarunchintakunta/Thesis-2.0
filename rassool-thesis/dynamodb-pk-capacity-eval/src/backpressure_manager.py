# Addresses Sharma et al. (2026) by introducing active backpressure 
# during burst loads to prevent cascading database failures
class DynamoBackpressureManager:
    def __init__(self, threshold_ops=1000):
        self.threshold = threshold_ops
        self.current_ops = 0

    def apply_backpressure(self, incoming_ops):
        # If operations exceed safety limits, reject early
        if self.current_ops + incoming_ops > self.threshold:
            rejected = (self.current_ops + incoming_ops) - self.threshold
            self.current_ops = self.threshold
            return {"status": "HTTP_429", "dropped": rejected}
        
        self.current_ops += incoming_ops
        return {"status": "HTTP_200", "dropped": 0}
