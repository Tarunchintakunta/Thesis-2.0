"""
Test benchmarking functionality.
"""

import pytest
import numpy as np
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from benchmark import (
    BenchmarkResult,
    MemoryMonitor,
    CPUMonitor,
    BenchmarkHarness
)
from matrix_operations import MultiThreadedOperations


class TestBenchmarkResult:
    """Test BenchmarkResult dataclass."""
    
    def test_benchmark_result_creation(self):
        """Test creating a benchmark result."""
        result = BenchmarkResult(
            config_name="test-config",
            matrix_size=100,
            n_workers=2,
            operation="matmul",
            parallelism_model="threaded",
            completion_time=1.23,
            peak_memory=456.78,
            avg_cpu_util=85.5,
            timestamp="2026-09-19T12:00:00"
        )
        
        assert result.config_name == "test-config"
        assert result.matrix_size == 100
        assert result.completion_time == 1.23
    
    def test_benchmark_result_to_dict(self):
        """Test converting result to dictionary."""
        result = BenchmarkResult(
            config_name="test",
            matrix_size=100,
            n_workers=2,
            operation="matmul",
            parallelism_model="threaded",
            completion_time=1.0,
            peak_memory=100.0,
            avg_cpu_util=50.0,
            timestamp="2026-09-19T12:00:00"
        )
        
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d['config_name'] == "test"
        assert d['completion_time'] == 1.0


class TestMemoryMonitor:
    """Test memory monitoring."""
    
    def test_memory_monitor_basic(self):
        """Test basic memory monitoring."""
        monitor = MemoryMonitor(interval=0.01)
        
        monitor.start()
        # Allocate some memory
        data = np.random.rand(1000, 1000)
        import time
        time.sleep(0.1)
        peak_mem = monitor.stop()
        
        assert peak_mem > 0, "Should have measured some memory"
        assert peak_mem < 100000, "Memory measurement seems wrong"


class TestCPUMonitor:
    """Test CPU monitoring."""
    
    def test_cpu_monitor_basic(self):
        """Test basic CPU monitoring."""
        monitor = CPUMonitor(interval=0.05)
        
        monitor.start()
        # Do some CPU work
        _ = np.random.rand(500, 500) @ np.random.rand(500, 500)
        avg_cpu = monitor.stop()
        
        assert avg_cpu >= 0, "CPU should be non-negative"
        assert avg_cpu <= 100, "CPU should not exceed 100%"


class TestBenchmarkHarness:
    """Test benchmark harness."""
    
    def test_harness_creation(self, tmp_path):
        """Test creating benchmark harness."""
        harness = BenchmarkHarness(output_dir=str(tmp_path))
        assert harness.output_dir.exists()
        assert len(harness.results) == 0
    
    def test_single_benchmark(self, tmp_path):
        """Test running a single benchmark."""
        harness = BenchmarkHarness(output_dir=str(tmp_path))
        
        # Simple test function
        def test_operation(A, B):
            return A @ B
        
        size = 50
        A = np.random.rand(size, size)
        B = np.random.rand(size, size)
        
        result = harness.run_single_benchmark(
            test_operation,
            "test-config",
            size, 1,
            "matmul",
            "threaded",
            A, B
        )
        
        assert isinstance(result, BenchmarkResult)
        assert result.completion_time > 0
        assert result.peak_memory > 0
    
    def test_repeated_benchmark(self, tmp_path):
        """Test running repeated benchmarks."""
        harness = BenchmarkHarness(output_dir=str(tmp_path))
        
        ops = MultiThreadedOperations(size=50, n_threads=1)
        A = ops.generate_matrix()
        B = ops.generate_matrix()
        
        stats = harness.run_repeated_benchmark(
            ops.matrix_multiply_threaded,
            "test-repeated",
            50, 1,
            "matmul",
            "threaded",
            3,  # n_iterations
            A, B
        )
        
        assert stats['n_iterations'] == 3
        assert 'mean_time' in stats
        assert 'std_time' in stats
        assert stats['mean_time'] > 0
    
    def test_save_results(self, tmp_path):
        """Test saving results to files."""
        harness = BenchmarkHarness(output_dir=str(tmp_path))
        
        # Add a dummy result
        result = BenchmarkResult(
            config_name="test",
            matrix_size=100,
            n_workers=1,
            operation="matmul",
            parallelism_model="threaded",
            completion_time=1.0,
            peak_memory=100.0,
            avg_cpu_util=50.0,
            timestamp="2026-09-19T12:00:00"
        )
        harness.results.append(result)
        
        # Save as JSON
        harness.save_results_json("test.json")
        json_file = tmp_path / "data" / "test.json"
        assert json_file.exists()
        
        # Verify contents
        with open(json_file) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]['config_name'] == "test"
        
        # Save as CSV
        harness.save_results_csv("test.csv")
        csv_file = tmp_path / "data" / "test.csv"
        assert csv_file.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
