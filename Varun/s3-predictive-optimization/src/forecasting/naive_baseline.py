"""
Naive persistence baseline for forecast evaluation.
Beck et al. (2025) - importance of naive baseline comparison.
"""

from typing import List
import numpy as np


class NaiveBaseline:
    """
    Naive persistence forecast: predicts that tomorrow's cost = today's cost.
    
    Reference: Beck, Dovern & Vogl (2025), "Mind the Naive Forecast!"
    Applied Intelligence, DOI: 10.1007/s10489-025-06268-w
    
    This baseline is essential to avoid inflated forecast accuracy claims.
    """
    
    def __init__(self):
        self.method = "naive_persistence"
    
    def forecast(self, historical_costs: List[float], horizon: int) -> List[float]:
        """
        Naive persistence forecast.
        
        Args:
            historical_costs: List of historical cost observations
            horizon: Number of periods to forecast
        
        Returns:
            List of forecasted values (all equal to last observed value)
        """
        if not historical_costs:
            return [0.0] * horizon
        
        last_value = historical_costs[-1]
        return [last_value] * horizon
    
    def calculate_error(self, actual: List[float], predicted: List[float]) -> dict:
        """Calculate forecast error metrics."""
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((actual - predicted) / (actual + 1e-10))) * 100
        
        # Root Mean Squared Error
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # Mean Absolute Error
        mae = np.mean(np.abs(actual - predicted))
        
        return {
            "mape": float(mape),
            "rmse": float(rmse),
            "mae": float(mae),
            "method": self.method
        }
    
    def get_metadata(self) -> dict:
        """Return baseline metadata."""
        return {
            "method": "naive_persistence",
            "description": "Forecasts that next period cost equals current period cost",
            "reference": "Beck, Dovern & Vogl (2025), Applied Intelligence",
            "doi": "10.1007/s10489-025-06268-w",
            "importance": "Essential baseline to avoid inflated accuracy claims"
        }
