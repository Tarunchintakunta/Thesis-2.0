"""Unit tests for QoS classification models."""
import pytest
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, '/workspace/uday-thesis/iot-reliability')

from src.models.qos_models import CentralizedRF, FederatedEnsembleRF
from src.data.qos_simulator import generate_all_sites, FEATURES


@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    sites = generate_all_sites(n_per_site=200, seed=42)
    return sites


def test_centralized_rf_training(sample_data):
    """Test that centralized RF can be trained."""
    sites = sample_data
    model = CentralizedRF(seed=42)
    model.fit(sites, FEATURES)
    
    # Check that model is trained
    assert model.model is not None
    assert hasattr(model.model, 'predict')


def test_centralized_rf_prediction(sample_data):
    """Test that centralized RF can make predictions."""
    sites = sample_data
    model = CentralizedRF(seed=42)
    model.fit(sites, FEATURES)
    
    # Make predictions on first site's data
    X = sites[list(sites.keys())[0]][FEATURES].values
    predictions = model.predict(X)
    
    # Predictions should have same length as input
    assert len(predictions) == len(X)
    
    # Predictions should be in {0, 1, 2}
    assert set(predictions).issubset({0, 1, 2})


def test_federated_ensemble_training(sample_data):
    """Test that federated ensemble can be trained."""
    sites = sample_data
    model = FederatedEnsembleRF(seed=42)
    model.fit(sites, FEATURES)
    
    # Check that all site models are trained
    assert len(model.site_models) == len(sites)
    for site_model in model.site_models.values():
        assert site_model is not None
        assert hasattr(site_model, 'predict')


def test_federated_ensemble_prediction(sample_data):
    """Test that federated ensemble can make predictions."""
    sites = sample_data
    model = FederatedEnsembleRF(seed=42)
    model.fit(sites, FEATURES)
    
    # Make predictions on first site's data
    X = sites[list(sites.keys())[0]][FEATURES].values
    predictions = model.predict(X)
    
    # Predictions should have same length as input
    assert len(predictions) == len(X)
    
    # Predictions should be in {0, 1, 2}
    assert set(predictions).issubset({0, 1, 2})


def test_federated_single_site_prediction(sample_data):
    """Test that federated ensemble can make single-site predictions."""
    sites = sample_data
    model = FederatedEnsembleRF(seed=42)
    model.fit(sites, FEATURES)
    
    # Make predictions using first site's model only
    site_name = list(sites.keys())[0]
    X = sites[site_name][FEATURES].values
    predictions = model.predict_single_site(site_name, X)
    
    # Predictions should have same length as input
    assert len(predictions) == len(X)
    
    # Predictions should be in {0, 1, 2}
    assert set(predictions).issubset({0, 1, 2})


def test_model_performance_above_baseline(sample_data):
    """Test that models achieve reasonable accuracy (>80%)."""
    sites = sample_data
    
    # Split each site's data into train/test
    from sklearn.model_selection import train_test_split
    train_sites = {}
    test_X = []
    test_y = []
    
    for site_name, df in sites.items():
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])
        train_sites[site_name] = train_df.reset_index(drop=True)
        test_X.append(test_df[FEATURES].values)
        test_y.append(test_df["label"].values)
    
    X_test = np.concatenate(test_X)
    y_test = np.concatenate(test_y)
    
    # Train centralized model
    cent_model = CentralizedRF(seed=42)
    cent_model.fit(train_sites, FEATURES)
    cent_acc = (cent_model.predict(X_test) == y_test).mean()
    
    # Should achieve >80% accuracy on synthetic data
    assert cent_acc > 0.80, f"Centralized model accuracy {cent_acc:.3f} below 80%"


def test_federated_comparable_to_centralized(sample_data):
    """Test that federated model is comparable to centralized."""
    sites = sample_data
    
    # Split each site's data into train/test
    from sklearn.model_selection import train_test_split
    train_sites = {}
    test_X = []
    test_y = []
    
    for site_name, df in sites.items():
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])
        train_sites[site_name] = train_df.reset_index(drop=True)
        test_X.append(test_df[FEATURES].values)
        test_y.append(test_df["label"].values)
    
    X_test = np.concatenate(test_X)
    y_test = np.concatenate(test_y)
    
    # Train both models
    cent_model = CentralizedRF(seed=42)
    cent_model.fit(train_sites, FEATURES)
    cent_acc = (cent_model.predict(X_test) == y_test).mean()
    
    fed_model = FederatedEnsembleRF(seed=42)
    fed_model.fit(train_sites, FEATURES)
    fed_acc = (fed_model.predict(X_test) == y_test).mean()
    
    # Federated should be within reasonable range of centralized
    assert fed_acc > 0.70, f"Federated model accuracy {fed_acc:.3f} below 70%"
    # Allow up to 30% gap since we're using small data (200 samples per site)
    assert abs(cent_acc - fed_acc) < 0.30, f"Federated ({fed_acc:.3f}) far from centralized ({cent_acc:.3f})"


def test_reproducibility():
    """Test that same seed produces same results."""
    sites = generate_all_sites(n_per_site=100, seed=123)
    
    # Train two models with same seed
    model1 = CentralizedRF(seed=456)
    model1.fit(sites, FEATURES)
    
    model2 = CentralizedRF(seed=456)
    model2.fit(sites, FEATURES)
    
    # Make predictions
    X = sites[list(sites.keys())[0]][FEATURES].values
    pred1 = model1.predict(X)
    pred2 = model2.predict(X)
    
    # Should produce same predictions
    assert np.array_equal(pred1, pred2)
