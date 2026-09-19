"""Synthetic S3 workload generator for local simulator."""

import random
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np


class WorkloadGenerator:
    """Generates synthetic S3 object access patterns."""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        self.current_time = datetime.now()
    
    def generate_objects(self, num_objects: int, config: Dict) -> List[Dict]:
        """Generate synthetic S3 objects with realistic characteristics."""
        objects = []
        
        # Parse access pattern distribution
        patterns = config.get("access_patterns", [{"hot": 0.2, "warm": 0.3, "cold": 0.5}])[0]
        hot_ratio = patterns.get("hot", 0.2)
        warm_ratio = patterns.get("warm", 0.3)
        cold_ratio = patterns.get("cold", 0.5)
        
        # Parse size distribution
        size_dist = config.get("size_distribution", {})
        mean_mb = size_dist.get("mean_mb", 10)
        std_mb = size_dist.get("std_mb", 5)
        min_mb = size_dist.get("min_mb", 0.1)
        max_mb = size_dist.get("max_mb", 100)
        
        for i in range(num_objects):
            # Determine access pattern category
            rand = random.random()
            if rand < hot_ratio:
                pattern = "hot"
                access_freq_range = (50, 200)  # accesses per month
                age_range = (1, 30)  # days
            elif rand < (hot_ratio + warm_ratio):
                pattern = "warm"
                access_freq_range = (5, 50)
                age_range = (30, 180)
            else:
                pattern = "cold"
                access_freq_range = (0, 5)
                age_range = (180, 720)  # up to 2 years
            
            # Generate object characteristics
            size_mb = np.clip(np.random.normal(mean_mb, std_mb), min_mb, max_mb)
            age_days = random.randint(*age_range)
            access_frequency = random.randint(*access_freq_range)
            
            # Calculate derived metrics
            creation_date = self.current_time - timedelta(days=age_days)
            last_access_days = random.randint(0, min(age_days, 30))
            
            obj = {
                "object_id": f"obj_{i:06d}",
                "key": f"data/test-object-{i:06d}.dat",
                "size_mb": round(size_mb, 2),
                "size_kb": round(size_mb * 1024, 2),
                "age_days": age_days,
                "creation_date": creation_date.isoformat(),
                "last_access_days": last_access_days,
                "access_frequency": access_frequency,  # per month
                "access_pattern": pattern,
                "current_storage_class": "STANDARD",  # all start in Standard
                "metadata": {
                    "content_type": "application/octet-stream",
                    "e_tag": f"etag_{i:06d}"
                }
            }
            
            objects.append(obj)
        
        return objects
    
    def generate_access_log(self, objects: List[Dict], days: int) -> List[Dict]:
        """Generate synthetic access log entries for objects over time period."""
        access_log = []
        
        for obj in objects:
            freq = obj["access_frequency"]
            pattern = obj["access_pattern"]
            
            # Generate access timestamps over the period
            if pattern == "hot":
                # Frequent, regular accesses
                num_accesses = int(freq * (days / 30))
                for _ in range(num_accesses):
                    access_time = self.current_time - timedelta(
                        days=random.randint(0, days)
                    )
                    access_log.append({
                        "object_id": obj["object_id"],
                        "timestamp": access_time.isoformat(),
                        "operation": random.choice(["GET", "GET", "HEAD"]),
                        "bytes_transferred": obj["size_mb"] * 1024 * 1024
                    })
            
            elif pattern == "warm":
                # Occasional accesses, clustered
                num_accesses = int(freq * (days / 30))
                for _ in range(num_accesses):
                    access_time = self.current_time - timedelta(
                        days=random.randint(0, days // 2)
                    )
                    access_log.append({
                        "object_id": obj["object_id"],
                        "timestamp": access_time.isoformat(),
                        "operation": random.choice(["GET", "HEAD"]),
                        "bytes_transferred": obj["size_mb"] * 1024 * 1024
                    })
            
            else:  # cold
                # Very rare accesses
                if random.random() < 0.3:  # 30% chance of any access
                    access_time = self.current_time - timedelta(
                        days=random.randint(days // 2, days)
                    )
                    access_log.append({
                        "object_id": obj["object_id"],
                        "timestamp": access_time.isoformat(),
                        "operation": "GET",
                        "bytes_transferred": obj["size_mb"] * 1024 * 1024
                    })
        
        # Sort by timestamp
        access_log.sort(key=lambda x: x["timestamp"])
        
        return access_log
