"""Tests for workload generation."""
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.workload_simulator import generate_workload


def test_workload_generation_deterministic():
    """Verify that the same seed produces the same workload."""
    workload1 = generate_workload(steps=100, seed=42)
    workload2 = generate_workload(steps=100, seed=42)
    np.testing.assert_array_equal(workload1, workload2)


def test_workload_generation_different_seeds():
    """Verify that different seeds produce different workloads."""
    workload1 = generate_workload(steps=100, seed=42)
    workload2 = generate_workload(steps=100, seed=43)
    assert not np.array_equal(workload1, workload2)


def test_workload_has_positive_values():
    """Ensure workload values are non-negative."""
    workload = generate_workload(steps=500, seed=42)
    assert np.all(workload >= 0), "Workload should have no negative values"


def test_workload_has_reasonable_bounds():
    """Ensure workload values are within reasonable bounds."""
    workload = generate_workload(steps=500, seed=42)
    # Based on actual implementation: base 1000±600, spikes 800-1500, noise ±300, clipped [100, 10000]
    assert np.all(workload >= 100), "Workload should respect floor of 100"
    assert np.all(workload <= 10000), "Workload should not exceed 10000"


def test_workload_has_variation():
    """Ensure workload is not constant."""
    workload = generate_workload(steps=500, seed=42)
    std_dev = np.std(workload)
    assert std_dev > 50, "Workload should have meaningful variation"


def test_workload_length():
    """Verify that generated workload has correct length."""
    for n in [100, 200, 500]:
        workload = generate_workload(steps=n, seed=42)
        assert len(workload) == n
