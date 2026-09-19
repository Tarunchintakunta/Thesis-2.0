"""Tests for recommendation engines."""

import pytest
from src.recommendation.baseline import BaselineRecommender
from src.pricing.s3_pricing import S3Pricing


@pytest.fixture
def sample_config():
    return {
        "baseline": {
            "age_threshold_ia": 30,
            "age_threshold_glacier_instant": 90,
            "age_threshold_glacier_deep": 180,
            "access_threshold_ia": 5,
            "access_threshold_glacier": 1,
            "size_threshold_kb": 128
        }
    }


@pytest.fixture
def sample_objects():
    return [
        {
            "object_id": "obj_001",
            "key": "test/hot.dat",
            "size_mb": 10,
            "size_kb": 10240,
            "age_days": 10,
            "access_frequency": 50,
            "last_access_days": 1,
            "current_storage_class": "STANDARD"
        },
        {
            "object_id": "obj_002",
            "key": "test/cold.dat",
            "size_mb": 100,
            "size_kb": 102400,
            "age_days": 200,
            "access_frequency": 0,
            "last_access_days": 180,
            "current_storage_class": "STANDARD"
        }
    ]


def test_baseline_recommender_initialization(sample_config):
    """Test baseline recommender initializes correctly."""
    recommender = BaselineRecommender(sample_config)
    assert recommender.age_threshold_ia == 30


def test_baseline_hot_object(sample_config, sample_objects):
    """Test baseline recommender handles hot objects."""
    recommender = BaselineRecommender(sample_config)
    hot_obj = sample_objects[0]
    
    recommendation = recommender.recommend_storage_class(hot_obj)
    assert recommendation == "STANDARD"


def test_baseline_cold_object(sample_config, sample_objects):
    """Test baseline recommender handles cold objects."""
    recommender = BaselineRecommender(sample_config)
    cold_obj = sample_objects[1]
    
    recommendation = recommender.recommend_storage_class(cold_obj)
    assert recommendation == "GLACIER_DEEP_ARCHIVE"


def test_baseline_batch(sample_config, sample_objects):
    """Test baseline batch recommendations."""
    recommender = BaselineRecommender(sample_config)
    recommendations = recommender.recommend_batch(sample_objects)
    
    assert len(recommendations) == 2
    assert all("recommended_storage_class" in r for r in recommendations)
