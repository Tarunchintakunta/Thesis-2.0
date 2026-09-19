"""
Time-series forecasting for S3 storage costs using Prophet.
"""

from typing import Dict, List
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    Prophet = None


class TimeSeriesForecaster:
    """
    Time-series cost forecasting using Prophet.
    
    Predicts future storage costs based on historical patterns.
    Includes seasonality, trend, and holiday effects.
    """
    
    def __init__(self, config: Dict):
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet not available. Install with: pip install prophet")
        
        self.config = config
        self.model = None
        self.trained = False
        
        self.horizon_days = config.get("horizon_days", 30)
        self.confidence_interval = config.get("confidence_interval", 0.95)
    
    def prepare_data(self, cost_history: List[Dict]) -> pd.DataFrame:
        """
        Prepare cost history for Prophet.
        
        Prophet requires columns: 'ds' (date) and 'y' (value)
        """
        if not cost_history:
            return pd.DataFrame({"ds": [], "y": []})
        
        df = pd.DataFrame(cost_history)
        
        # Ensure we have date and cost columns
        if "date" in df.columns and "cost" in df.columns:
            df = df.rename(columns={"date": "ds", "cost": "y"})
        elif "ds" not in df.columns or "y" not in df.columns:
            raise ValueError("Cost history must have 'date'/'ds' and 'cost'/'y' columns")
        
        # Convert to datetime
        df["ds"] = pd.to_datetime(df["ds"])
        df["y"] = pd.to_numeric(df["y"])
        
        return df[["ds", "y"]].sort_values("ds")
    
    def train(self, cost_history: List[Dict]) -> Dict:
        """Train Prophet model on historical cost data."""
        df = self.prepare_data(cost_history)
        
        if len(df) < 2:
            raise ValueError("Need at least 2 historical data points for forecasting")
        
        # Initialize Prophet with configuration
        self.model = Prophet(
            interval_width=self.confidence_interval,
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=False
        )
        
        # Train model
        self.model.fit(df)
        self.trained = True
        
        return {
            "training_points": len(df),
            "start_date": str(df["ds"].min()),
            "end_date": str(df["ds"].max()),
            "method": "prophet"
        }
    
    def forecast(self, periods: int = None) -> pd.DataFrame:
        """Generate forecast for specified number of periods."""
        if not self.trained:
            raise ValueError("Model not trained. Call train() first.")
        
        if periods is None:
            periods = self.horizon_days
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods, freq='D')
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    
    def forecast_cost(self, cost_history: List[Dict], horizon_days: int = None) -> Dict:
        """
        Full forecast pipeline: train and predict.
        
        Returns:
            Dictionary with forecast, confidence intervals, and metadata
        """
        if horizon_days is None:
            horizon_days = self.horizon_days
        
        # Train model
        train_info = self.train(cost_history)
        
        # Generate forecast
        forecast_df = self.forecast(horizon_days)
        
        # Extract future predictions only (not historical fit)
        last_historical_date = pd.to_datetime(cost_history[-1].get("date") or 
                                             cost_history[-1].get("ds"))
        future_forecast = forecast_df[forecast_df["ds"] > last_historical_date]
        
        # Convert to JSON-serializable format
        future_forecast_dict = future_forecast.copy()
        future_forecast_dict["ds"] = future_forecast_dict["ds"].dt.strftime("%Y-%m-%d")
        
        return {
            "forecast": future_forecast_dict.to_dict("records"),
            "horizon_days": horizon_days,
            "train_info": train_info,
            "method": "prophet",
            "confidence_interval": self.confidence_interval
        }
    
    def calculate_error(self, actual: List[float], predicted: List[float]) -> Dict:
        """Calculate forecast error metrics."""
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # Ensure same length
        min_len = min(len(actual), len(predicted))
        actual = actual[:min_len]
        predicted = predicted[:min_len]
        
        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((actual - predicted) / (actual + 1e-10))) * 100
        
        # Root Mean Squared Error
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # Mean Absolute Error
        mae = np.mean(np.abs(actual - predicted))
        
        # R-squared
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        r2 = 1 - (ss_res / (ss_tot + 1e-10))
        
        return {
            "mape": float(mape),
            "rmse": float(rmse),
            "mae": float(mae),
            "r2": float(r2),
            "method": "prophet"
        }
    
    def get_metadata(self) -> Dict:
        """Return forecaster metadata."""
        return {
            "method": "prophet",
            "library": "Facebook Prophet",
            "horizon_days": self.horizon_days,
            "confidence_interval": self.confidence_interval,
            "trained": self.trained
        }
