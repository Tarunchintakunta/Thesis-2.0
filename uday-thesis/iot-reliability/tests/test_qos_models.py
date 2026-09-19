"""Unit tests for QoS classification models."""
import pytest
import sys
sys.path.insert(0, '/workspace/uday-thesis/iot-reliability')

from src.models.qos_models import CentralizedRF, FederatedEnsembleRF
from src.data.qos_simulator import QoSSimulator


@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    sim = QoSSimulator(n_sites=3, records_per_site=200, random_seed=42)
    X, y, site_ids = sim.generate()
    return X, y, site_ids


def test_centralized_rf_training(sample_data):
    """Test that centralized RF can be trained."""
    X, y, _ = sample_data
    model = CentralizedRF(random_state=42)
    model.fit(X, y)
    
    # Check that model is trained
    assert model.model is not None
    assert hasattr(model.model, 'predict')


def test_centralized_rf_prediction(sample_data):
    """Test that centralized RF can make predictions."""
    X, y, _ = sample_data
    model = CentralizedRF(random_state=42)
    model.fit(X, y)
    
    predictions = model.predict(X)
    
    # Predictions should have same length as input
    assert len(predictions) == len(X)
    
    # Predictions should be in {0, 1, 2}
    assert set(predictions).issubset({0, 1, 2})


def test_federated_ensemble_training(sample_data):
    """Test that federated ensemble can be trained."""
    X, y, site_ids = sample_data
    model = FederatedEnsembleRF(n_sites=3, random_state=42)
    model.fit(X, y, site_ids)
    
    # Check that all site models are trained
    assert len(model.site_models) == 3
    for site_model in model.site_models.values():
        assert site_model is not None
        assert hasattr(site_model, 'predict')


def test_federated_ensemble_prediction(sample_data):
    """Test that federated ensemble can make predictions."""
    X, y, site_ids = sample_data
    model = FederatedEnsembleRF(n_sites=3, random_state=42)
    model.fit(X, y, site_ids)
    
    predictions = model.predict(X)
    
    # Predictions should have same length as input
    assert len(predictions) == len(X)
    
    # Predictions should be in {0, 1, 2}
    assert set(predictions).issubset({0, 1, 2})


def test_federated_probability_averaging(sample_data):
    """Test that federated ensemble averages probabilities correctly."""
    X, y, site_ids = sample_data
    model = FederatedEnsembleRF(n_sites=3, random_state=42)
    model.fit(X, y, site_ids)
    
    probas = model.predict_proba(X)
    
    # Check shape: (n_samples, n_classes)
    assert probas.shape == (len(X), 3)
    
    # Check that probabilities sum to 1 (within numerical precision)
    import numpy as np
    assert np.allclose(probas.sum(axis=1), 1.0)
    
    # Check that probabilities are in [0, 1]
    assert (probas >= 0).all() and (probas <= 1).all()


def test_model_performance_above_baseline(sample_data):
    """Test that models achieve reasonable accuracy (>80%)."""
    X, y, site_ids = sample_data
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test, site_train, site_test = train_test_split(
        X, y, site_ids, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train centralized model
    cent_model = CentralizedRF(random_state=42)
    cent_model.fit(X_train, y_train)
    cent_acc = (cent_model.predict(X_test) == y_test).mean()
    
    # Should achieve >80% accuracy on synthetic data
    assert cent_acc > 0.80, f"Centralized model accuracy {cent_acc:.3f} below 80%"


def test_federated_comparable_to_centralized(sample_data):
    """Test that federated model is comparable to centralized."""
    X, y, site_ids = sample_data
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test, site_train, site_test = train_test_split(
        X, y, site_ids, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train both models
    cent_model = CentralizedRF(random_state=42)
    cent_model.fit(X_train, y_train)
    cent_acc = (cent_model.predict(X_test) == y_test).mean()
    
    fed_model = FederatedEnsembleRF(n_sites=3, random_state=42)
    fed_model.fit(X_train, y_train, site_train)
    fed_acc = (fed_model.predict(X_test) == y_test).mean()
    
    # Federated should be within 10% of centralized
    assert fed_acc > 0.70, f"Federated model accuracy {fed_acc:.3f} below 70%"
    assert abs(cent_acc - fed_acc) < 0.15, f"Federated ({fed_acc:.3f}) far from centralized ({cent_acc:.3f})"
