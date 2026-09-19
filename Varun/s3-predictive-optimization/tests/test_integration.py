"""Integration tests for full experiment."""

import pytest
import yaml
from pathlib import Path
from src.runner.experiment import ExperimentRunner


@pytest.fixture
def pilot_config():
    config_path = Path(__file__).parent.parent / "configs" / "pilot.yaml"
    return str(config_path)


def test_experiment_runner_initialization(pilot_config):
    """Test experiment runner initializes with config."""
    runner = ExperimentRunner(pilot_config)
    assert runner.experiment_name == "pilot"
    assert runner.pricing is not None


def test_workload_generation(pilot_config):
    """Test synthetic workload generation."""
    runner = ExperimentRunner(pilot_config)
    objects, access_log = runner.generate_workload()
    
    assert len(objects) > 0
    assert len(access_log) >= 0
    assert all("object_id" in obj for obj in objects)


def test_baseline_recommendation_run(pilot_config):
    """Test baseline recommendation runs."""
    runner = ExperimentRunner(pilot_config)
    objects, _ = runner.generate_workload()
    
    recommendations = runner.run_baseline_recommendation(objects)
    
    assert len(recommendations) == len(objects)
    assert all("recommended_storage_class" in r for r in recommendations)


def test_cost_history_generation(pilot_config):
    """Test cost history generation."""
    runner = ExperimentRunner(pilot_config)
    objects, _ = runner.generate_workload()
    
    cost_history = runner.generate_cost_history(objects, days=30)
    
    assert len(cost_history) == 30
    assert all("date" in h and "cost" in h for h in cost_history)
