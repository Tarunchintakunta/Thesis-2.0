"""Tests for savings estimator."""

import pytest
from src.savings.estimator import SavingsEstimator
from src.pricing.s3_pricing import S3Pricing


@pytest.fixture
def sample_object():
    return {
        "object_id": "obj_001",
        "key": "test/data.dat",
        "size_mb": 100,
        "size_kb": 102400,
        "age_days": 90,
        "access_frequency": 2,
        "current_storage_class": "STANDARD"
    }


@pytest.fixture
def sample_recommendation():
    return {
        "object_id": "obj_001",
        "current_storage_class": "STANDARD",
        "recommended_storage_class": "GLACIER_INSTANT"
    }


def test_estimator_initialization():
    """Test savings estimator initializes."""
    estimator = SavingsEstimator()
    assert estimator.pricing is not None


def test_object_cost_calculation(sample_object):
    """Test object cost calculation."""
    estimator = SavingsEstimator()
    cost = estimator.calculate_object_cost(sample_object, "STANDARD", months=1)
    assert cost > 0


def test_savings_single(sample_object, sample_recommendation):
    """Test single object savings estimation."""
    estimator = SavingsEstimator()
    savings = estimator.estimate_savings_single(sample_object, sample_recommendation)
    
    assert "savings_usd_monthly" in savings
    assert "savings_percent" in savings
    assert savings["savings_usd_monthly"] > 0  # Should save by moving to Glacier


def test_savings_batch(sample_object, sample_recommendation):
    """Test batch savings estimation."""
    estimator = SavingsEstimator()
    objects = [sample_object]
    recommendations = [sample_recommendation]
    
    savings = estimator.estimate_savings_batch(objects, recommendations)
    
    assert "total_savings_usd_monthly" in savings
    assert savings["num_objects"] == 1
