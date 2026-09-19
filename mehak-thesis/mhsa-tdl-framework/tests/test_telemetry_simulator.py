"""
Tests for telemetry simulator.
"""
import numpy as np
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.telemetry_simulator import TelemetrySimulator, TelemetryDataset, METRIC_NAMES


class TestTelemetrySimulator:
    """Test suite for TelemetrySimulator."""

    def test_initialization(self):
        """Test simulator initialization with valid parameters."""
        sim = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        assert sim.num_samples == 100
        assert sim.seq_length == 10
        assert sim.transient_ratio == 0.4
        assert sim.seed == 42

    def test_data_generation_shape(self):
        """Test that generated data has correct shapes."""
        sim = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        
        # X should be (num_samples, seq_length, num_metrics)
        assert X.shape == (100, 10, 4)
        # y should be (num_samples, num_metrics)
        assert y.shape == (100, 4)
        # is_transient should be (num_samples,)
        assert is_transient.shape == (100,)
        
    def test_data_generation_types(self):
        """Test that generated data has correct types."""
        sim = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        
        assert X.dtype in [np.float32, np.float64]  # Accept either float type
        assert y.dtype == np.int64
        assert is_transient.dtype == bool

    def test_transient_ratio(self):
        """Test that transient ratio is approximately correct."""
        sim = TelemetrySimulator(num_samples=1000, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        
        actual_ratio = is_transient.sum() / len(is_transient)
        # Allow 10% tolerance
        assert 0.35 <= actual_ratio <= 0.45

    def test_metric_range(self):
        """Test that metric values are in valid range [0, 1]."""
        sim = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        
        assert np.all(X >= 0.0)
        assert np.all(X <= 1.0)

    def test_label_values(self):
        """Test that labels are in valid range {0, 1, 2}."""
        sim = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        
        assert np.all(y >= 0)
        assert np.all(y <= 2)

    def test_reproducibility(self):
        """Test that same seed produces same data."""
        sim1 = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X1, y1, is_transient1 = sim1.generate_data()
        
        sim2 = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X2, y2, is_transient2 = sim2.generate_data()
        
        np.testing.assert_array_equal(X1, X2)
        np.testing.assert_array_equal(y1, y2)
        np.testing.assert_array_equal(is_transient1, is_transient2)

    def test_different_seeds_produce_different_data(self):
        """Test that different seeds produce different data."""
        sim1 = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X1, y1, is_transient1 = sim1.generate_data()
        
        sim2 = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=43)
        X2, y2, is_transient2 = sim2.generate_data()
        
        # Data should be different
        assert not np.array_equal(X1, X2)


class TestTelemetryDataset:
    """Test suite for TelemetryDataset."""

    def test_dataset_length(self):
        """Test dataset length."""
        sim = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        dataset = TelemetryDataset(X, y, is_transient)
        
        assert len(dataset) == 100

    def test_dataset_getitem(self):
        """Test dataset __getitem__."""
        sim = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        dataset = TelemetryDataset(X, y, is_transient)
        
        sample_X, sample_y, sample_transient = dataset[0]
        
        assert sample_X.shape == (10, 4)
        assert sample_y.shape == (4,)
        assert isinstance(sample_transient.item(), bool)


class TestMetricNames:
    """Test metric names constant."""

    def test_metric_names(self):
        """Test that metric names are correct."""
        assert METRIC_NAMES == ['cpu', 'mem', 'disk', 'net']
        assert len(METRIC_NAMES) == 4
