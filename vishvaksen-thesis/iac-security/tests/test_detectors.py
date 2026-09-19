"""
Unit tests for the ML, rule-based, and hybrid detectors.
"""
import pytest
import numpy as np
from src.models.detectors import MLDetector, HybridDetector, rule_based_flag, RULE_PATTERNS


class TestRuleBasedDetector:
    """Test suite for rule-based detection."""
    
    def test_rule_detects_world_writable_permissions(self):
        snippet = 'resource "deploy_directory" {\n  mode = "0777"\n}'
        assert rule_based_flag(snippet) == True
    
    def test_rule_detects_http_protocol(self):
        snippet = 'resource "api_endpoint" {\n  protocol = "http"\n}'
        assert rule_based_flag(snippet) == True
    
    def test_rule_detects_weak_hash(self):
        snippet = 'resource "auth_service" {\n  hash_algorithm = "sha1"\n}'
        assert rule_based_flag(snippet) == True
        
        snippet_md5 = 'resource "auth_service" {\n  hash_algorithm = "md5"\n}'
        assert rule_based_flag(snippet_md5) == True
    
    def test_rule_detects_world_open_ingress(self):
        snippet = 'resource "security_group" {\n  ingress_cidr = "0.0.0.0/0"\n}'
        assert rule_based_flag(snippet) == True
    
    def test_rule_ignores_safe_config(self):
        snippet = 'resource "deploy_directory" {\n  mode = "0640"\n}'
        assert rule_based_flag(snippet) == False
        
        snippet_https = 'resource "api_endpoint" {\n  protocol = "https"\n}'
        assert rule_based_flag(snippet_https) == False
    
    def test_rule_ignores_hard_pattern(self):
        # Hard patterns use opaque references - rules cannot detect them
        snippet = 'resource "credential_store" {\n  password_ref = "ref_12345"\n}'
        assert rule_based_flag(snippet) == False
    
    def test_all_rule_patterns_are_valid(self):
        # Ensure all compiled regexes are valid
        assert len(RULE_PATTERNS) == 4
        for pattern in RULE_PATTERNS:
            assert pattern.pattern is not None


class TestMLDetector:
    """Test suite for ML detector."""
    
    def test_ml_detector_training(self):
        snippets = [
            'resource "test" {\n  mode = "0777"\n}',
            'resource "test" {\n  mode = "0640"\n}',
            'resource "test" {\n  protocol = "http"\n}',
            'resource "test" {\n  protocol = "https"\n}',
        ]
        labels = np.array([1, 0, 1, 0])
        
        detector = MLDetector()
        detector.fit(snippets, labels)
        
        # Verify model is trained
        assert detector.vectorizer is not None
        assert detector.model is not None
    
    def test_ml_detector_prediction(self):
        train_snippets = [
            'resource "test" {\n  mode = "0777"\n}',
            'resource "test" {\n  mode = "0640"\n}',
            'resource "test" {\n  protocol = "http"\n}',
            'resource "test" {\n  protocol = "https"\n}',
        ] * 10  # Duplicate for stable training
        train_labels = np.array([1, 0, 1, 0] * 10)
        
        detector = MLDetector()
        detector.fit(train_snippets, train_labels)
        
        # Test predictions
        test_snippets = [
            'resource "test" {\n  mode = "0777"\n}',
            'resource "test" {\n  mode = "0640"\n}',
        ]
        predictions = detector.predict(test_snippets)
        
        assert len(predictions) == 2
        assert predictions[0] == 1  # Vulnerable
        assert predictions[1] == 0  # Safe
    
    def test_ml_detector_predict_proba(self):
        train_snippets = [
            'resource "test" {\n  mode = "0777"\n}',
            'resource "test" {\n  mode = "0640"\n}',
        ] * 20
        train_labels = np.array([1, 0] * 20)
        
        detector = MLDetector()
        detector.fit(train_snippets, train_labels)
        
        test_snippets = ['resource "test" {\n  mode = "0777"\n}']
        probas = detector.predict_proba(test_snippets)
        
        assert len(probas) == 1
        assert 0 <= probas[0] <= 1


class TestHybridDetector:
    """Test suite for hybrid detector."""
    
    def test_hybrid_detector_uses_rule_layer(self):
        # Train a dummy ML detector
        train_snippets = [
            'resource "test" {\n  mode = "0777"\n}',
            'resource "test" {\n  mode = "0640"\n}',
        ] * 20
        train_labels = np.array([1, 0] * 20)
        
        ml_detector = MLDetector()
        ml_detector.fit(train_snippets, train_labels)
        
        hybrid = HybridDetector(ml_detector, ml_threshold=0.8)
        
        # Rule-detectable pattern should be flagged
        test_snippet = 'resource "test" {\n  mode = "0777"\n}'
        prediction = hybrid.predict([test_snippet])
        
        assert prediction[0] == 1
    
    def test_hybrid_detector_thresholding(self):
        train_snippets = [
            'resource "test" {\n  mode = "0777"\n}',
            'resource "test" {\n  mode = "0640"\n}',
            'resource "test" {\n  hash_algorithm = "sha1"\n}',
            'resource "test" {\n  hash_algorithm = "sha256"\n}',
        ] * 20
        train_labels = np.array([1, 0, 1, 0] * 20)
        
        ml_detector = MLDetector()
        ml_detector.fit(train_snippets, train_labels)
        
        # Test different thresholds
        hybrid_low = HybridDetector(ml_detector, ml_threshold=0.5)
        hybrid_high = HybridDetector(ml_detector, ml_threshold=0.9)
        
        # Both should detect rule-based patterns
        rule_snippet = ['resource "test" {\n  mode = "0777"\n}']
        assert hybrid_low.predict(rule_snippet)[0] == 1
        assert hybrid_high.predict(rule_snippet)[0] == 1
    
    def test_hybrid_detector_default_threshold(self):
        train_snippets = [
            'resource "test" {\n  mode = "0777"\n}',
            'resource "test" {\n  mode = "0640"\n}',
        ] * 10
        train_labels = np.array([1, 0] * 10)
        
        ml_detector = MLDetector()
        ml_detector.fit(train_snippets, train_labels)
        
        # Default threshold should be 0.8
        hybrid = HybridDetector(ml_detector)
        assert hybrid.ml_threshold == 0.8


class TestDatasetIntegration:
    """Integration tests with the dataset generator."""
    
    def test_dataset_generation(self):
        from src.data.iac_dataset import generate_dataset
        
        snippets, labels = generate_dataset(n_samples=100, seed=42, with_comments=True)
        
        assert len(snippets) == 100
        assert len(labels) == 100
        assert all(label in [0, 1] for label in labels)
    
    def test_comment_stripping_consistency(self):
        from src.data.iac_dataset import generate_dataset
        
        rich_snippets, rich_labels = generate_dataset(n_samples=50, seed=42, with_comments=True)
        plain_snippets, plain_labels = generate_dataset(n_samples=50, seed=42, with_comments=False)
        
        # Labels should be identical for the same seed
        assert np.array_equal(rich_labels, plain_labels)
        
        # Snippets should differ (comments present vs. absent)
        assert rich_snippets != plain_snippets
    
    def test_end_to_end_pipeline(self):
        from src.data.iac_dataset import generate_dataset
        
        # Generate dataset
        snippets, labels = generate_dataset(n_samples=200, seed=42, with_comments=True)
        
        # Split train/test
        from sklearn.model_selection import train_test_split
        idx_train, idx_test = train_test_split(
            np.arange(200), test_size=0.3, random_state=42, stratify=labels
        )
        
        train_snippets = [snippets[i] for i in idx_train]
        test_snippets = [snippets[i] for i in idx_test]
        train_labels = labels[idx_train]
        test_labels = labels[idx_test]
        
        # Train ML detector
        ml_detector = MLDetector()
        ml_detector.fit(train_snippets, train_labels)
        
        # Create hybrid detector
        hybrid = HybridDetector(ml_detector)
        
        # Make predictions
        predictions = hybrid.predict(test_snippets)
        
        assert len(predictions) == len(test_labels)
        assert all(pred in [0, 1] for pred in predictions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
