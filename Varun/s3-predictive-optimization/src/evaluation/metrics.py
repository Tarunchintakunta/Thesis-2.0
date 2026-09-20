"""
Evaluation metrics for the S3 predictive optimization framework.
"""

from typing import Dict, List
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from scipy import stats


class MetricsCalculator:
    """Calculate evaluation metrics for recommendations and forecasts."""
    
    @staticmethod
    def allocation_accuracy(y_true: List[str], y_pred: List[str]) -> float:
        """Calculate storage class allocation accuracy."""
        return accuracy_score(y_true, y_pred)
    
    @staticmethod
    def classification_metrics(y_true: List[str], y_pred: List[str]) -> Dict:
        """Calculate precision, recall, F1 for storage class classification."""
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        
        return {
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "accuracy": MetricsCalculator.allocation_accuracy(y_true, y_pred)
        }
    
    @staticmethod
    def forecast_mape(actual: List[float], predicted: List[float]) -> float:
        """Calculate Mean Absolute Percentage Error."""
        actual = np.array(actual)
        predicted = np.array(predicted)
        return float(np.mean(np.abs((actual - predicted) / (actual + 1e-10))) * 100)
    
    @staticmethod
    def forecast_rmse(actual: List[float], predicted: List[float]) -> float:
        """Calculate Root Mean Squared Error."""
        actual = np.array(actual)
        predicted = np.array(predicted)
        return float(np.sqrt(np.mean((actual - predicted) ** 2)))
    
    @staticmethod
    def forecast_mae(actual: List[float], predicted: List[float]) -> float:
        """Calculate Mean Absolute Error."""
        actual = np.array(actual)
        predicted = np.array(predicted)
        return float(np.mean(np.abs(actual - predicted)))
    
    @staticmethod
    def cost_savings_metrics(current_cost: float, optimized_cost: float) -> Dict:
        """Calculate cost savings metrics."""
        savings_usd = current_cost - optimized_cost
        savings_pct = (savings_usd / (current_cost + 1e-10)) * 100
        
        return {
            "current_cost_usd": float(current_cost),
            "optimized_cost_usd": float(optimized_cost),
            "savings_usd": float(savings_usd),
            "savings_percent": float(savings_pct)
        }
    
    @staticmethod
    def wilcoxon_test(sample1: List[float], sample2: List[float], 
                     alpha: float = 0.05) -> Dict:
        """
        Perform Wilcoxon signed-rank test.
        
        Tests if there's a statistically significant difference between
        paired samples (e.g., baseline vs improved method costs).
        """
        if len(sample1) != len(sample2):
            raise ValueError("Samples must have equal length for paired test")
        
        if len(sample1) < 5:
            return {
                "test": "wilcoxon",
                "statistic": None,
                "p_value": None,
                "significant": False,
                "note": "Sample size too small (n < 5)"
            }
        
        statistic, p_value = stats.wilcoxon(sample1, sample2, alternative='two-sided')
        
        return {
            "test": "wilcoxon",
            "statistic": float(statistic),
            "p_value": float(p_value),
            "alpha": alpha,
            "significant": bool(p_value < alpha),
            "n": len(sample1)
        }
    
    @staticmethod
    def comprehensive_evaluation(recommendations: List[Dict], 
                                actual_optimal: List[str],
                                forecast_actual: List[float],
                                forecast_predicted: List[float],
                                forecast_naive: List[float],
                                savings_data: Dict) -> Dict:
        """
        Comprehensive evaluation combining all metrics.
        """
        # Extract predicted classes
        predicted = [r["recommended_storage_class"] for r in recommendations]
        
        # Classification metrics
        classification = MetricsCalculator.classification_metrics(actual_optimal, predicted)
        
        # Forecast metrics - our method vs actual
        forecast_metrics = {
            "mape": MetricsCalculator.forecast_mape(forecast_actual, forecast_predicted),
            "rmse": MetricsCalculator.forecast_rmse(forecast_actual, forecast_predicted),
            "mae": MetricsCalculator.forecast_mae(forecast_actual, forecast_predicted)
        }
        
        # Naive baseline comparison
        naive_metrics = {
            "mape": MetricsCalculator.forecast_mape(forecast_actual, forecast_naive),
            "rmse": MetricsCalculator.forecast_rmse(forecast_actual, forecast_naive),
            "mae": MetricsCalculator.forecast_mae(forecast_actual, forecast_naive)
        }
        
        # Check if we beat naive baseline
        beats_naive = {
            "mape": forecast_metrics["mape"] < naive_metrics["mape"],
            "rmse": forecast_metrics["rmse"] < naive_metrics["rmse"],
            "mae": forecast_metrics["mae"] < naive_metrics["mae"]
        }
        
        return {
            "allocation": classification,
            "forecast": {
                "our_method": forecast_metrics,
                "naive_baseline": naive_metrics,
                "beats_naive_baseline": beats_naive,
                "improvement_vs_naive_mape_pct": float(
                    ((naive_metrics["mape"] - forecast_metrics["mape"]) / 
                     (naive_metrics["mape"] + 1e-10)) * 100
                )
            },
            "cost_savings": savings_data
        }
