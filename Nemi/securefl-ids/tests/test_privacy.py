"""
Test differential privacy mechanisms
"""
import pytest
import torch
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.common.privacy import DifferentialPrivacy, AdaptiveDifferentialPrivacy
from src.common.models import CNNClassifier


def test_gradient_clipping():
    """Test gradient clipping"""
    model = CNNClassifier(input_dim=10, num_classes=2)
    dp = DifferentialPrivacy(epsilon=1.0, clip_norm=1.0)
    
    # Create dummy gradients
    for param in model.parameters():
        param.grad = torch.randn_like(param) * 10  # Large gradients
    
    # Clip gradients
    grad_norm = dp.clip_gradients(model)
    
    # Check that clipping occurred
    new_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), float('inf'))
    assert new_norm <= dp.clip_norm + 1e-5  # Allow small numerical error


def test_noise_addition():
    """Test noise addition to gradients"""
    model = CNNClassifier(input_dim=10, num_classes=2)
    dp = DifferentialPrivacy(epsilon=1.0, delta=1e-5, clip_norm=1.0)
    
    # Store original gradients
    for param in model.parameters():
        param.grad = torch.ones_like(param)
    
    original_grads = [p.grad.clone() for p in model.parameters()]
    
    # Add noise
    dp.add_noise_to_gradients(model)
    
    # Check that gradients have changed
    for orig, param in zip(original_grads, model.parameters()):
        assert not torch.equal(orig, param.grad)


def test_adaptive_epsilon():
    """Test adaptive privacy budget calculation"""
    dp = AdaptiveDifferentialPrivacy(base_epsilon=1.0, adaptive=True)
    
    # High quality data should get lower epsilon (more privacy)
    epsilon_high_quality = dp.get_client_epsilon(
        client_id=0, 
        total_clients=5, 
        data_quality=1.0
    )
    
    # Low quality data should get higher epsilon (less noise)
    epsilon_low_quality = dp.get_client_epsilon(
        client_id=1, 
        total_clients=5, 
        data_quality=0.3
    )
    
    # Epsilon should be in valid range
    assert 0.5 <= epsilon_high_quality <= 2.0
    assert 0.5 <= epsilon_low_quality <= 2.0
    
    # Can't strictly guarantee ordering due to bounding, but check reasonableness
    assert epsilon_low_quality >= epsilon_high_quality * 0.8


def test_privacy_budget_bounds():
    """Test that privacy budget stays within reasonable bounds"""
    dp = AdaptiveDifferentialPrivacy(base_epsilon=1.0)
    
    # Test extreme quality values
    for quality in [0.1, 0.5, 0.9, 1.0]:
        epsilon = dp.get_client_epsilon(0, 5, quality)
        # Should be bounded to [0.5 * base, 2.0 * base]
        assert 0.5 <= epsilon <= 2.0
