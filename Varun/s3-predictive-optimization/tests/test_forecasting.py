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


def test_cost_history_retains_variance():
    """Sub-cent daily costs must not collapse to a flat series (beats_naive hygiene)."""
    from src.runner.experiment import ExperimentRunner

    runner = ExperimentRunner("configs/pilot.yaml")
    objects, _ = runner.generate_workload()
    history = runner.generate_cost_history(objects, days=60)
    costs = [h["cost"] for h in history]
    assert len(set(round(c, 8) for c in costs)) > 1
    assert max(costs) > min(costs)


def test_forecast_holdout_protocol_fields():
    """Holdout protocol must expose eval_protocol and comparable MAPEs."""
    from src.runner.experiment import ExperimentRunner

    runner = ExperimentRunner("configs/pilot.yaml")
    objects, _ = runner.generate_workload()
    history = runner.generate_cost_history(objects, days=60)
    data = runner.run_forecasting(history)
    assert data is not None
    fc = runner.results["forecasting"]
    assert fc.get("eval_protocol") == "temporal_holdout"
    assert "beats_naive_baseline" in fc
    assert fc["prophet"]["errors"]["mape"] >= 0
    assert fc["naive_baseline"]["errors"]["mape"] >= 0
