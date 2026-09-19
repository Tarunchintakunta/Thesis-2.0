"""
Test data loading and preprocessing
"""
import pytest
import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.common.data_loader import UNSWDataLoader, create_federated_data


def test_unsw_data_loader():
    """Test basic data loading"""
    # This test assumes data has been downloaded
    if not os.path.exists("data/UNSW_NB15_training-set.csv"):
        pytest.skip("Dataset not available")
    
    loader = UNSWDataLoader()
    X, y = loader.load_data(binary=True, sample_size=1000)
    
    assert X.shape[0] == 1000
    assert y.shape[0] == 1000
    assert X.shape[1] > 0
    assert len(np.unique(y)) == 2  # Binary classification


def test_non_iid_split():
    """Test non-IID data distribution"""
    # Create synthetic data
    X = np.random.randn(1000, 10)
    y = np.random.randint(0, 2, 1000)
    
    loader = UNSWDataLoader()
    client_data = loader.create_non_iid_split(X, y, num_clients=5, alpha=0.5)
    
    assert len(client_data) == 5
    
    total_samples = sum(len(X_c) for X_c, y_c in client_data)
    assert total_samples == 1000
    
    # Check non-IID property (clients have different class distributions)
    class_ratios = []
    for X_c, y_c in client_data:
        if len(y_c) > 0:
            ratio = np.mean(y_c)
            class_ratios.append(ratio)
    
    # Standard deviation should be > 0 for non-IID
    assert np.std(class_ratios) > 0


def test_normalization():
    """Test feature normalization"""
    X_train = np.random.randn(100, 10)
    X_test = np.random.randn(50, 10)
    
    loader = UNSWDataLoader()
    X_train_scaled, X_test_scaled = loader.normalize(X_train, X_test)
    
    assert X_train_scaled.shape == X_train.shape
    assert X_test_scaled.shape == X_test.shape
    
    # Check approximate zero mean and unit variance for training set
    assert np.abs(X_train_scaled.mean()) < 0.1
    assert np.abs(X_train_scaled.std() - 1.0) < 0.1
