"""AWS S3 pricing data and utilities."""

import json
import os
from typing import Dict


class S3Pricing:
    """AWS S3 storage class pricing information."""
    
    def __init__(self, pricing_file: str = None):
        if pricing_file is None:
            pricing_file = os.path.join(
                os.path.dirname(__file__), "..", "..", "configs", "pricing.json"
            )
        
        with open(pricing_file, 'r') as f:
            self.pricing_data = json.load(f)
        
        self.storage_classes = self.pricing_data["storage_classes"]
    
    def get_storage_cost_per_month(self, storage_class: str, size_gb: float) -> float:
        """Calculate monthly storage cost for given size in GB."""
        if storage_class not in self.storage_classes:
            raise ValueError(f"Unknown storage class: {storage_class}")
        
        pricing = self.storage_classes[storage_class]
        return size_gb * pricing["storage_gb_month"]
    
    def get_retrieval_cost(self, storage_class: str, num_requests: int = 0, 
                          size_gb: float = 0) -> float:
        """Calculate retrieval cost based on storage class."""
        if storage_class not in self.storage_classes:
            raise ValueError(f"Unknown storage class: {storage_class}")
        
        pricing = self.storage_classes[storage_class]
        cost = 0.0
        
        if "retrieval_per_1000" in pricing:
            cost += (num_requests / 1000) * pricing["retrieval_per_1000"]
        
        if "retrieval_per_gb" in pricing:
            cost += size_gb * pricing["retrieval_per_gb"]
        
        if "monitoring_per_1000" in pricing:
            cost += (num_requests / 1000) * pricing["monitoring_per_1000"]
        
        return cost
    
    def get_total_cost(self, storage_class: str, size_gb: float, 
                      num_accesses: int, months: int = 1) -> float:
        """Calculate total cost (storage + retrieval) for a period."""
        storage_cost = self.get_storage_cost_per_month(storage_class, size_gb) * months
        retrieval_cost = self.get_retrieval_cost(storage_class, num_accesses, size_gb)
        return storage_cost + retrieval_cost
    
    def get_min_storage_days(self, storage_class: str) -> int:
        """Get minimum storage duration requirement for storage class."""
        if storage_class not in self.storage_classes:
            return 0
        return self.storage_classes[storage_class].get("min_storage_days", 0)
    
    def get_min_object_size_kb(self, storage_class: str) -> int:
        """Get minimum object size requirement for storage class."""
        if storage_class not in self.storage_classes:
            return 0
        return self.storage_classes[storage_class].get("min_object_size_kb", 0)
    
    def is_valid_for_class(self, storage_class: str, size_kb: float, 
                          age_days: int) -> bool:
        """Check if object meets requirements for storage class."""
        if storage_class not in self.storage_classes:
            return False
        
        pricing = self.storage_classes[storage_class]
        
        min_size = pricing.get("min_object_size_kb", 0)
        if size_kb < min_size:
            return False
        
        min_days = pricing.get("min_storage_days", 0)
        if age_days < min_days:
            return False
        
        return True
