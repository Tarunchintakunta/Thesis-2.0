"""
Baseline recommendation engine based on TierBase methodology.
Shen et al. (2025), TierBase: A Workload-Driven Cost-Optimized Key-Value Store, ICDE 2025
DOI: 10.1109/ICDE65448.2025.00049
"""

from typing import Dict, List
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.pricing.s3_pricing import S3Pricing


class BaselineRecommender:
    """
    TierBase-inspired rule-based storage class recommender.
    
    Uses age, access frequency, and size thresholds to recommend optimal
    storage class following TierBase's workload-driven cost optimization approach.
    """
    
    def __init__(self, config: Dict, pricing: S3Pricing = None):
        self.config = config.get("baseline", {})
        self.pricing = pricing or S3Pricing()
        
        # Thresholds from config (TierBase-inspired)
        self.age_threshold_ia = self.config.get("age_threshold_ia", 30)
        self.age_threshold_glacier_instant = self.config.get("age_threshold_glacier_instant", 90)
        self.age_threshold_glacier_deep = self.config.get("age_threshold_glacier_deep", 180)
        
        self.access_threshold_ia = self.config.get("access_threshold_ia", 5)
        self.access_threshold_glacier = self.config.get("access_threshold_glacier", 1)
        
        self.size_threshold_kb = self.config.get("size_threshold_kb", 128)
    
    def recommend_storage_class(self, obj: Dict) -> str:
        """
        Recommend optimal storage class for an object based on TierBase methodology.
        
        Rules:
        1. Hot data (frequent access) → STANDARD
        2. Warm data (infrequent access, recent) → STANDARD_IA
        3. Cold data (rare access, old) → GLACIER_INSTANT
        4. Archive data (very old, no access) → GLACIER_DEEP_ARCHIVE
        """
        age_days = obj.get("age_days", 0)
        access_freq = obj.get("access_frequency", 0)  # accesses per month
        last_access_days = obj.get("last_access_days", age_days)
        size_kb = obj.get("size_kb", 0)
        
        # Rule 1: Very small objects stay in STANDARD (avoid minimum size charges)
        if size_kb < self.size_threshold_kb:
            return "STANDARD"
        
        # Rule 2: Frequently accessed → STANDARD
        if access_freq > self.access_threshold_ia:
            return "STANDARD"
        
        # Rule 3: Recently accessed but infrequent → STANDARD_IA
        if (last_access_days < self.age_threshold_ia and 
            age_days >= self.age_threshold_ia and
            access_freq > 0):
            return "STANDARD_IA"
        
        # Rule 4: Old but occasionally accessed → GLACIER_INSTANT
        if (age_days >= self.age_threshold_glacier_instant and
            age_days < self.age_threshold_glacier_deep and
            access_freq <= self.access_threshold_glacier and
            access_freq > 0):
            return "GLACIER_INSTANT"
        
        # Rule 5: Very old with no recent access → GLACIER_DEEP_ARCHIVE
        if age_days >= self.age_threshold_glacier_deep:
            return "GLACIER_DEEP_ARCHIVE"
        
        # Rule 6: Middle-aged, rarely accessed → GLACIER_FLEXIBLE
        if (age_days >= self.age_threshold_glacier_instant and
            access_freq <= self.access_threshold_glacier):
            return "GLACIER_FLEXIBLE"
        
        # Default: STANDARD_IA for everything else meeting minimum age
        if age_days >= self.age_threshold_ia:
            return "STANDARD_IA"
        
        return "STANDARD"
    
    def recommend_batch(self, objects: List[Dict]) -> List[Dict]:
        """Recommend storage classes for a batch of objects."""
        recommendations = []
        
        for obj in objects:
            recommended_class = self.recommend_storage_class(obj)
            current_class = obj.get("current_storage_class", "STANDARD")
            
            recommendations.append({
                "object_id": obj["object_id"],
                "key": obj["key"],
                "current_storage_class": current_class,
                "recommended_storage_class": recommended_class,
                "age_days": obj.get("age_days", 0),
                "access_frequency": obj.get("access_frequency", 0),
                "size_kb": obj.get("size_kb", 0),
                "reason": self._get_recommendation_reason(obj, recommended_class)
            })
        
        return recommendations
    
    def _get_recommendation_reason(self, obj: Dict, recommended_class: str) -> str:
        """Generate human-readable reason for recommendation."""
        age = obj.get("age_days", 0)
        freq = obj.get("access_frequency", 0)
        size_kb = obj.get("size_kb", 0)
        
        if size_kb < self.size_threshold_kb:
            return f"Too small ({size_kb:.1f} KB < {self.size_threshold_kb} KB threshold)"
        
        if recommended_class == "STANDARD":
            if freq > self.access_threshold_ia:
                return f"Frequently accessed ({freq} accesses/month)"
            return "Recently created or frequently accessed"
        
        if recommended_class == "STANDARD_IA":
            return f"Infrequent access ({freq} accesses/month), age {age} days"
        
        if recommended_class == "GLACIER_INSTANT":
            return f"Rare access, age {age} days (optimal for instant retrieval archive)"
        
        if recommended_class == "GLACIER_FLEXIBLE":
            return f"Very rare access ({freq} accesses/month), age {age} days"
        
        if recommended_class == "GLACIER_DEEP_ARCHIVE":
            return f"Long-term archive, age {age} days"
        
        return "Rule-based recommendation"
    
    def get_metadata(self) -> Dict:
        """Return recommender metadata."""
        return {
            "method": "baseline_tierbase",
            "reference": "Shen et al. (2025), TierBase, ICDE 2025",
            "doi": "10.1109/ICDE65448.2025.00049",
            "thresholds": {
                "age_threshold_ia": self.age_threshold_ia,
                "age_threshold_glacier_instant": self.age_threshold_glacier_instant,
                "age_threshold_glacier_deep": self.age_threshold_glacier_deep,
                "access_threshold_ia": self.access_threshold_ia,
                "access_threshold_glacier": self.access_threshold_glacier,
                "size_threshold_kb": self.size_threshold_kb
            }
        }
