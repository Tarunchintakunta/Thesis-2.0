"""Tests for forecasting modules."""

import pytest
from src.forecasting.naive_baseline import NaiveBaseline


def test_naive_baseline_forecast():
    """Test naive persistence forecast."""
    naive = NaiveBaseline()
    historical = [10.0, 12.0, 11.0, 13.0]
    
    forecast = naive.forecast(historical, horizon=5)
    
    assert len(forecast) == 5
    assert all(f == 13.0 for f in forecast)  # All equal to last value


def test_naive_baseline_error():
    """Test naive baseline error calculation."""
    naive = NaiveBaseline()
    
    actual = [10.0, 11.0, 12.0]
    predicted = [10.0, 10.0, 10.0]
    
    errors = naive.calculate_error(actual, predicted)
    
    assert "mape" in errors
    assert "rmse" in errors
    assert errors["mape"] > 0


def test_naive_baseline_metadata():
    """Test naive baseline metadata."""
    naive = NaiveBaseline()
    metadata = naive.get_metadata()
    
    assert metadata["method"] == "naive_persistence"
    assert "Beck" in metadata["reference"]
