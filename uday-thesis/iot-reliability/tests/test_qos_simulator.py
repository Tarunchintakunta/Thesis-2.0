"""Unit tests for QoS telemetry simulator."""
import pytest
import sys
sys.path.insert(0, '/workspace/uday-thesis/iot-reliability')

from src.data.qos_simulator import QoSSimulator


def test_simulator_initialization():
    """Test that simulator initializes correctly."""
    sim = QoSSimulator(n_sites=6, records_per_site=100, random_seed=42)
    assert sim.n_sites == 6
    assert sim.records_per_site == 100


def test_generate_data_shape():
    """Test that generated data has correct shape."""
    sim = QoSSimulator(n_sites=3, records_per_site=50, random_seed=42)
    X, y, site_ids = sim.generate()
    
    # Total records = n_sites * records_per_site
    assert X.shape[0] == 150
    assert y.shape[0] == 150
    assert len(site_ids) == 150
    
    # 6 features per record
    assert X.shape[1] == 6


def test_label_distribution():
    """Test that labels follow expected distribution."""
    sim = QoSSimulator(n_sites=6, records_per_site=1000, random_seed=42)
    _, y, _ = sim.generate()
    
    # Count each class
    unique, counts = pytest.importorskip('numpy').unique(y, return_counts=True)
    
    # Should have 3 classes (0, 1, 2)
    assert len(unique) == 3
    assert set(unique) == {0, 1, 2}
    
    # Class 2 (Critical) should be minority (~10%)
    class_2_ratio = counts[2] / len(y)
    assert 0.05 < class_2_ratio < 0.20  # Flexible range


def test_non_iid_site_distributions():
    """Test that each site has different (non-IID) traffic distribution."""
    sim = QoSSimulator(n_sites=6, records_per_site=500, random_seed=42)
    X, y, site_ids = sim.generate()
    
    import numpy as np
    
    # Extract class distributions per site
    site_distributions = []
    for site_id in range(6):
        site_mask = site_ids == site_id
        site_labels = y[site_mask]
        unique, counts = np.unique(site_labels, return_counts=True)
        dist = {int(label): count / len(site_labels) for label, count in zip(unique, counts)}
        site_distributions.append(dist)
    
    # Check that not all sites have identical distributions
    # (Non-IID property: sites should differ)
    first_dist = site_distributions[0]
    all_same = all(dist == first_dist for dist in site_distributions[1:])
    assert not all_same, "All sites have identical distributions (not non-IID)"


def test_feature_ranges():
    """Test that generated features are within expected ranges."""
    sim = QoSSimulator(n_sites=3, records_per_site=200, random_seed=42)
    X, _, _ = sim.generate()
    
    # RTT should be positive
    assert (X[:, 0] >= 0).all()
    
    # CPU and RAM should be in [0, 100]
    assert (X[:, 1] >= 0).all() and (X[:, 1] <= 100).all()
    assert (X[:, 2] >= 0).all() and (X[:, 2] <= 100).all()
    
    # Success rate should be in [0, 100]
    assert (X[:, 3] >= 0).all() and (X[:, 3] <= 100).all()
    
    # Latency should be positive
    assert (X[:, 4] >= 0).all()
    
    # Throughput should be positive
    assert (X[:, 5] >= 0).all()


def test_reproducibility():
    """Test that same seed produces same data."""
    sim1 = QoSSimulator(n_sites=3, records_per_site=100, random_seed=123)
    X1, y1, site_ids1 = sim1.generate()
    
    sim2 = QoSSimulator(n_sites=3, records_per_site=100, random_seed=123)
    X2, y2, site_ids2 = sim2.generate()
    
    import numpy as np
    assert np.array_equal(X1, X2)
    assert np.array_equal(y1, y2)
    assert np.array_equal(site_ids1, site_ids2)
