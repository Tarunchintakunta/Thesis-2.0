"""
Savings estimation module.
Calculates expected cost savings before applying recommendations.
"""

from typing import Dict, List
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.pricing.s3_pricing import S3Pricing


class SavingsEstimator:
    """
    Estimates cost savings from storage class recommendations.
    
    Compares:
    - Current (unoptimized) cost
    - Recommended storage class cost
    - AWS Lifecycle Policies baseline
    - AWS Intelligent-Tiering baseline
    """
    
    def __init__(self, pricing: S3Pricing = None):
        self.pricing = pricing or S3Pricing()
    
    def calculate_object_cost(self, obj: Dict, storage_class: str, 
                            months: int = 1) -> float:
        """Calculate total cost for an object in a given storage class."""
        size_gb = obj.get("size_mb", 0) / 1024
        access_freq = obj.get("access_frequency", 0)
        
        return self.pricing.get_total_cost(storage_class, size_gb, access_freq, months)
    
    def estimate_savings_single(self, obj: Dict, recommendation: Dict) -> Dict:
        """Estimate savings for a single object recommendation."""
        current_class = recommendation["current_storage_class"]
        recommended_class = recommendation["recommended_storage_class"]
        
        # Calculate costs for 1 month
        current_cost = self.calculate_object_cost(obj, current_class, months=1)
        recommended_cost = self.calculate_object_cost(obj, recommended_class, months=1)
        
        savings_usd = current_cost - recommended_cost
        savings_pct = (savings_usd / (current_cost + 1e-10)) * 100
        
        return {
            "object_id": obj["object_id"],
            "current_cost_monthly": current_cost,
            "recommended_cost_monthly": recommended_cost,
            "savings_usd_monthly": savings_usd,
            "savings_percent": savings_pct,
            "current_class": current_class,
            "recommended_class": recommended_class
        }
    
    def estimate_savings_batch(self, objects: List[Dict], 
                              recommendations: List[Dict]) -> Dict:
        """Estimate aggregate savings for batch of recommendations."""
        total_current_cost = 0.0
        total_recommended_cost = 0.0
        individual_savings = []
        
        for obj, rec in zip(objects, recommendations):
            savings = self.estimate_savings_single(obj, rec)
            individual_savings.append(savings)
            
            total_current_cost += savings["current_cost_monthly"]
            total_recommended_cost += savings["recommended_cost_monthly"]
        
        total_savings = total_current_cost - total_recommended_cost
        savings_percent = (total_savings / (total_current_cost + 1e-10)) * 100
        
        return {
            "total_current_cost_monthly": total_current_cost,
            "total_recommended_cost_monthly": total_recommended_cost,
            "total_savings_usd_monthly": total_savings,
            "total_savings_percent": savings_percent,
            "num_objects": len(objects),
            "individual_savings": individual_savings
        }
    
    def compare_against_lifecycle(self, objects: List[Dict]) -> Dict:
        """
        Simulate AWS Lifecycle Policies baseline.
        
        Simple age-based rules:
        - < 30 days: STANDARD
        - 30-90 days: STANDARD_IA
        - > 90 days: GLACIER_FLEXIBLE
        """
        total_cost = 0.0
        
        for obj in objects:
            age = obj.get("age_days", 0)
            
            if age < 30:
                storage_class = "STANDARD"
            elif age < 90:
                storage_class = "STANDARD_IA"
            else:
                storage_class = "GLACIER_FLEXIBLE"
            
            total_cost += self.calculate_object_cost(obj, storage_class, months=1)
        
        return {
            "method": "aws_lifecycle_policies",
            "total_cost_monthly": total_cost,
            "description": "Age-based rules: <30d→STANDARD, 30-90d→IA, >90d→GLACIER"
        }
    
    def compare_against_intelligent_tiering(self, objects: List[Dict]) -> Dict:
        """
        Simulate AWS Intelligent-Tiering baseline.
        
        Uses access patterns to tier objects automatically.
        """
        total_cost = 0.0
        
        for obj in objects:
            # Intelligent-Tiering monitors access and moves between tiers
            # Simplified simulation based on access frequency
            freq = obj.get("access_frequency", 0)
            
            if freq > 10:
                effective_class = "STANDARD"
            else:
                effective_class = "STANDARD_IA"  # Simulated infrequent tier
            
            size_gb = obj.get("size_mb", 0) / 1024
            storage_cost = self.pricing.get_storage_cost_per_month(effective_class, size_gb)
            
            # Add monitoring fee
            monitoring_cost = 0.0025 * (obj.get("access_frequency", 0) / 1000)
            
            total_cost += storage_cost + monitoring_cost
        
        return {
            "method": "aws_intelligent_tiering",
            "total_cost_monthly": total_cost,
            "description": "Automatic tiering with monitoring fees"
        }
    
    def comprehensive_comparison(self, objects: List[Dict], 
                                recommendations: List[Dict]) -> Dict:
        """
        Compare recommended approach against all baselines.
        """
        # Our recommendation
        our_savings = self.estimate_savings_batch(objects, recommendations)
        
        # AWS Lifecycle baseline
        lifecycle = self.compare_against_lifecycle(objects)
        
        # AWS Intelligent-Tiering baseline
        intelligent = self.compare_against_intelligent_tiering(objects)
        
        # Calculate relative savings
        our_cost = our_savings["total_recommended_cost_monthly"]
        
        savings_vs_lifecycle = lifecycle["total_cost_monthly"] - our_cost
        savings_vs_intelligent = intelligent["total_cost_monthly"] - our_cost
        
        return {
            "our_approach": {
                "cost_monthly": our_cost,
                "savings_vs_unoptimized": our_savings["total_savings_usd_monthly"],
                "savings_percent": our_savings["total_savings_percent"]
            },
            "aws_lifecycle_policies": {
                "cost_monthly": lifecycle["total_cost_monthly"],
                "savings_vs_our_approach": -savings_vs_lifecycle,  # negative = we save more
                "description": lifecycle["description"]
            },
            "aws_intelligent_tiering": {
                "cost_monthly": intelligent["total_cost_monthly"],
                "savings_vs_our_approach": -savings_vs_intelligent,
                "description": intelligent["description"]
            },
            "num_objects": len(objects)
        }
    
    def get_metadata(self) -> Dict:
        """Return estimator metadata."""
        return {
            "method": "delta_pricing",
            "description": "Cost delta calculation using AWS Pricing API",
            "baselines": [
                "current_unoptimized",
                "aws_lifecycle_policies",
                "aws_intelligent_tiering"
            ]
        }
