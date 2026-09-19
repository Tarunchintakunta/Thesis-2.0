"""Tests for S3 pricing module."""

import pytest
from src.pricing.s3_pricing import S3Pricing


def test_pricing_initialization():
    """Test pricing data loads correctly."""
    pricing = S3Pricing()
    assert "STANDARD" in pricing.storage_classes
    assert "GLACIER_DEEP_ARCHIVE" in pricing.storage_classes


def test_storage_cost_calculation():
    """Test storage cost calculation."""
    pricing = S3Pricing()
    cost = pricing.get_storage_cost_per_month("STANDARD", 100)  # 100 GB
    assert cost == pytest.approx(2.3, rel=0.01)  # $0.023 * 100


def test_retrieval_cost():
    """Test retrieval cost calculation."""
    pricing = S3Pricing()
    cost = pricing.get_retrieval_cost("STANDARD", num_requests=1000)
    assert cost > 0


def test_total_cost():
    """Test total cost calculation."""
    pricing = S3Pricing()
    cost = pricing.get_total_cost("STANDARD", 10, 100, months=1)
    assert cost > 0


def test_validation():
    """Test storage class validation."""
    pricing = S3Pricing()
    
    # STANDARD has no restrictions
    assert pricing.is_valid_for_class("STANDARD", 10, 1)
    
    # STANDARD_IA requires 128 KB minimum
    assert not pricing.is_valid_for_class("STANDARD_IA", 100, 40)
    assert pricing.is_valid_for_class("STANDARD_IA", 128, 40)
