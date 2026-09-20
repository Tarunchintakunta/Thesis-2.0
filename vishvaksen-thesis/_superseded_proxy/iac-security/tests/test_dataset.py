"""
Unit tests for the synthetic IaC dataset generator.
"""
import pytest
import numpy as np
from src.data.iac_dataset import (
    generate_dataset,
    EASY_PATTERNS,
    HARD_PATTERNS,
    FILLER_LINES,
    _render_filler,
)


class TestFillerRendering:
    """Test filler line rendering."""
    
    def test_render_filler_length(self):
        rng = np.random.RandomState(42)
        filler = _render_filler(rng)
        assert len(filler) == len(FILLER_LINES)
    
    def test_render_filler_no_placeholders(self):
        rng = np.random.RandomState(42)
        filler = _render_filler(rng)
        
        for line in filler:
            # Check no unrendered placeholders remain (e.g., {name}, {region})
            # Allow dict syntax like {"env": "staging"}
            assert "{name}" not in line
            assert "{region}" not in line
            assert "{owner}" not in line
            assert "{env}" not in line
            assert "{itype}" not in line
            assert "{retention}" not in line
    
    def test_render_filler_randomness(self):
        rng1 = np.random.RandomState(42)
        rng2 = np.random.RandomState(43)
        
        filler1 = _render_filler(rng1)
        filler2 = _render_filler(rng2)
        
        # Different seeds should produce different results
        assert filler1 != filler2


class TestPatternDefinitions:
    """Test pattern structure."""
    
    def test_easy_patterns_structure(self):
        assert len(EASY_PATTERNS) == 4
        
        for pattern in EASY_PATTERNS:
            assert "resource" in pattern
            assert "unsafe" in pattern
            assert "safe" in pattern
            assert "comment_unsafe" in pattern
            assert "comment_safe" in pattern
    
    def test_hard_patterns_structure(self):
        assert len(HARD_PATTERNS) == 2
        
        for pattern in HARD_PATTERNS:
            assert "resource" in pattern
            assert "field" in pattern
            assert "comment_unsafe" in pattern
            assert "comment_safe" in pattern
    
    def test_easy_patterns_distinguishable(self):
        # Easy patterns should have different unsafe/safe values
        for pattern in EASY_PATTERNS:
            assert pattern["unsafe"] != pattern["safe"]
    
    def test_pattern_comments_differ(self):
        for pattern in EASY_PATTERNS + HARD_PATTERNS:
            assert pattern["comment_unsafe"] != pattern["comment_safe"]
            assert "WARNING" in pattern["comment_unsafe"]


class TestDatasetGeneration:
    """Test synthetic dataset generation."""
    
    def test_generate_dataset_size(self):
        snippets, labels = generate_dataset(n_samples=100, seed=42, with_comments=True)
        
        assert len(snippets) == 100
        assert len(labels) == 100
    
    def test_generate_dataset_labels_binary(self):
        snippets, labels = generate_dataset(n_samples=100, seed=42, with_comments=True)
        
        assert all(label in [0, 1] for label in labels)
    
    def test_generate_dataset_label_distribution(self):
        # With sufficient samples, should be roughly balanced
        snippets, labels = generate_dataset(n_samples=1000, seed=42, with_comments=True)
        
        n_positive = np.sum(labels)
        n_negative = len(labels) - n_positive
        
        # Should be within 30% of 50/50
        assert 0.35 < n_positive / len(labels) < 0.65
    
    def test_generate_dataset_with_comments(self):
        snippets, labels = generate_dataset(n_samples=20, seed=42, with_comments=True)
        
        # At least some snippets should contain comments (marked by '#')
        has_comments = [('#' in snippet) for snippet in snippets]
        assert any(has_comments)
    
    def test_generate_dataset_without_comments(self):
        snippets, labels = generate_dataset(n_samples=20, seed=42, with_comments=False)
        
        # No snippets should contain comments
        has_comments = [('#' in snippet) for snippet in snippets]
        assert not any(has_comments)
    
    def test_generate_dataset_reproducibility(self):
        snippets1, labels1 = generate_dataset(n_samples=50, seed=42, with_comments=True)
        snippets2, labels2 = generate_dataset(n_samples=50, seed=42, with_comments=True)
        
        assert snippets1 == snippets2
        assert np.array_equal(labels1, labels2)
    
    def test_generate_dataset_different_seeds(self):
        snippets1, labels1 = generate_dataset(n_samples=50, seed=42, with_comments=True)
        snippets2, labels2 = generate_dataset(n_samples=50, seed=43, with_comments=True)
        
        # Different seeds should produce different results
        assert snippets1 != snippets2
    
    def test_generate_dataset_paired_consistency(self):
        # Same seed with/without comments should have same labels
        rich_snippets, rich_labels = generate_dataset(n_samples=100, seed=42, with_comments=True)
        plain_snippets, plain_labels = generate_dataset(n_samples=100, seed=42, with_comments=False)
        
        assert np.array_equal(rich_labels, plain_labels)
    
    def test_snippet_contains_resource_block(self):
        snippets, labels = generate_dataset(n_samples=10, seed=42, with_comments=True)
        
        for snippet in snippets:
            assert 'resource "' in snippet
            assert '{' in snippet
            assert '}' in snippet
    
    def test_snippet_contains_filler_lines(self):
        snippets, labels = generate_dataset(n_samples=10, seed=42, with_comments=True)
        
        # At least some common filler patterns should appear
        has_region = any('region =' in s for s in snippets)
        has_owner = any('owner =' in s for s in snippets)
        
        assert has_region or has_owner
    
    def test_hard_pattern_uses_ref_format(self):
        # Hard patterns should use "ref_NNNNN" format
        snippets, labels = generate_dataset(n_samples=100, seed=42, with_comments=False)
        
        ref_snippets = [s for s in snippets if 'ref_' in s]
        
        # Should have some hard patterns
        assert len(ref_snippets) > 0
        
        # Check ref format
        for snippet in ref_snippets:
            assert 'ref_' in snippet
            # Extract ref and check it's numeric after "ref_"
            import re
            refs = re.findall(r'ref_(\d+)', snippet)
            assert len(refs) > 0
            assert all(ref.isdigit() and len(ref) == 5 for ref in refs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
