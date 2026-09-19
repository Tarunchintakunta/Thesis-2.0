"""Tests for scaling policies."""
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.workload_simulator import generate_workload
from src.models.scalers import (
    train_predictor,
    run_reactive_hpa,
    run_aggressive_paks,
    run_stability_aware_paks,
    StabilityAwareController
)


def test_train_predictor_runs():
    """Verify that predictor training completes without errors."""
    workload = generate_workload(steps=200, seed=42)
    model = train_predictor(workload, seed=42)
    assert model is not None
    
    # Test prediction
    test_input = workload[:10].reshape(1, -1)
    prediction = model.predict(test_input)
    assert len(prediction) == 1
    assert prediction[0] > 0


def test_reactive_hpa_runs():
    """Confirm that Reactive HPA runs without errors."""
    workload = generate_workload(steps=100, seed=42)
    pods = run_reactive_hpa(workload)
    
    assert len(pods) == len(workload)
    assert np.all(pods >= 1)  # At least 1 pod always


def test_aggressive_paks_uses_predictor():
    """Check that Aggressive PAKS produces valid allocations."""
    workload = generate_workload(steps=200, seed=42)
    model = train_predictor(workload, seed=42)
    
    pods_hpa = run_reactive_hpa(workload)
    pods_agg = run_aggressive_paks(workload, model)
    
    # Both should produce valid pod arrays
    assert len(pods_hpa) == len(workload)
    assert len(pods_agg) == len(workload)
    assert np.all(pods_hpa >= 1)
    assert np.all(pods_agg >= 1)


def test_stability_controller_basic():
    """Validate that StabilityAwareController works."""
    from src.data.workload_simulator import calculate_desired_pods
    workload = generate_workload(steps=100, seed=42)
    
    initial_pods = calculate_desired_pods(workload[0], 0.7)
    controller = StabilityAwareController(
        initial_pods=initial_pods,
        smoothing=0.4, 
        hysteresis_pods=1, 
        cooldown_steps=2
    )
    
    # Step through some predictions
    for t in range(10):
        raw_pred = workload[t]
        pods = controller.step(raw_pred)
        assert pods >= 1


def test_stability_aware_paks_runs():
    """Confirm that Stability-Aware PAKS runs without errors."""
    workload = generate_workload(steps=200, seed=42)
    model = train_predictor(workload, seed=42)
    
    pods = run_stability_aware_paks(workload, model)
    
    assert len(pods) == len(workload)
    assert np.all(pods >= 1)


def test_all_policies_produce_arrays():
    """Verify that all policies return numpy arrays of correct length."""
    workload = generate_workload(steps=150, seed=43)
    model = train_predictor(workload, seed=43)
    
    pods_hpa = run_reactive_hpa(workload)
    pods_agg = run_aggressive_paks(workload, model)
    pods_stab = run_stability_aware_paks(workload, model)
    
    for pods in [pods_hpa, pods_agg, pods_stab]:
        assert isinstance(pods, np.ndarray)
        assert len(pods) == len(workload)
        assert pods.dtype in [np.int64, np.int32, np.float64, np.float32]
