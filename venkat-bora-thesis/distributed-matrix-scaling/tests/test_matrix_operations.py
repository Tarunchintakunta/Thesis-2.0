"""
Test suite for matrix operations and benchmarking.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from matrix_operations import (
    MultiThreadedOperations,
    MultiProcessOperations,
    DistributedOperations,
    get_memory_usage,
    get_cpu_percent
)


class TestMatrixOperations:
    """Test basic matrix operations."""
    
    def test_matrix_generation(self):
        """Test matrix generation is reproducible."""
        ops1 = MultiThreadedOperations(size=100, seed=42)
        ops2 = MultiThreadedOperations(size=100, seed=42)
        
        A1 = ops1.generate_matrix()
        A2 = ops2.generate_matrix()
        
        assert np.allclose(A1, A2), "Matrices should be identical with same seed"
    
    def test_positive_definite_generation(self):
        """Test positive definite matrix generation."""
        ops = MultiThreadedOperations(size=50)
        A = ops.generate_positive_definite()
        
        # Check it's symmetric
        assert np.allclose(A, A.T), "Should be symmetric"
        
        # Check positive definiteness via eigenvalues
        eigenvalues = np.linalg.eigvals(A)
        assert np.all(eigenvalues > 0), "All eigenvalues should be positive"


class TestMultiThreadedOperations:
    """Test multi-threaded matrix operations."""
    
    @pytest.mark.parametrize("n_threads", [1, 2, 4])
    def test_matrix_multiply_threaded(self, n_threads):
        """Test threaded matrix multiplication."""
        size = 100
        ops = MultiThreadedOperations(size=size, n_threads=n_threads, seed=42)
        
        A = ops.generate_matrix()
        B = ops.generate_matrix()
        
        # Compute with threading
        C_threaded = ops.matrix_multiply_threaded(A, B)
        
        # Compute with NumPy (reference)
        C_numpy = A @ B
        
        # Check correctness
        assert C_threaded.shape == (size, size), "Output shape incorrect"
        assert np.allclose(C_threaded, C_numpy, rtol=1e-5), \
            f"Result differs from NumPy with {n_threads} threads"
    
    @pytest.mark.parametrize("n_threads", [1, 2])
    def test_lu_factorization_threaded(self, n_threads):
        """Test threaded LU factorization."""
        size = 50
        ops = MultiThreadedOperations(size=size, n_threads=n_threads, seed=42)
        
        A = ops.generate_positive_definite()
        L, U = ops.lu_factorization_threaded(A)
        
        # Check shapes
        assert L.shape == (size, size), "L shape incorrect"
        assert U.shape == (size, size), "U shape incorrect"
        
        # Check L is lower triangular
        assert np.allclose(L, np.tril(L)), "L should be lower triangular"
        
        # Check U is upper triangular
        assert np.allclose(U, np.triu(U)), "U should be upper triangular"
        
        # Check reconstruction: A ≈ L @ U
        A_reconstructed = L @ U
        assert np.allclose(A, A_reconstructed, rtol=1e-4), \
            "LU reconstruction failed"


class TestMultiProcessOperations:
    """Test multi-process matrix operations."""
    
    @pytest.mark.parametrize("n_processes", [1, 2])
    def test_matrix_multiply_multiprocess(self, n_processes):
        """Test multiprocess matrix multiplication."""
        size = 100
        ops = MultiProcessOperations(size=size, n_processes=n_processes, seed=42)
        
        A = ops.generate_matrix()
        B = ops.generate_matrix()
        
        # Compute with multiprocessing
        C_mp = ops.matrix_multiply_multiprocess(A, B)
        
        # Compute with NumPy (reference)
        C_numpy = A @ B
        
        # Check correctness
        assert C_mp.shape == (size, size), "Output shape incorrect"
        assert np.allclose(C_mp, C_numpy, rtol=1e-5), \
            f"Result differs from NumPy with {n_processes} processes"


class TestDistributedOperations:
    """Test distributed matrix operations with Dask."""
    
    @pytest.mark.timeout(30)
    def test_distributed_setup_teardown(self):
        """Test Dask cluster setup and shutdown."""
        ops = DistributedOperations(size=100, n_workers=2)
        
        try:
            client = ops.setup_cluster()
            assert client is not None, "Client should be created"
            assert len(client.scheduler_info()['workers']) == 2, \
                "Should have 2 workers"
        finally:
            ops.shutdown_cluster()
    
    @pytest.mark.timeout(60)
    def test_matrix_multiply_distributed(self):
        """Test distributed matrix multiplication."""
        size = 100
        ops = DistributedOperations(size=size, n_workers=2, seed=42)
        
        try:
            ops.setup_cluster()
            
            A = ops.generate_matrix()
            B = ops.generate_matrix()
            
            # Compute with Dask
            C_dask = ops.matrix_multiply_distributed(A, B)
            
            # Compute with NumPy (reference)
            C_numpy = A @ B
            
            # Check correctness
            assert C_dask.shape == (size, size), "Output shape incorrect"
            assert np.allclose(C_dask, C_numpy, rtol=1e-5), \
                "Distributed result differs from NumPy"
        
        finally:
            ops.shutdown_cluster()
    
    @pytest.mark.timeout(60)
    def test_lu_factorization_distributed(self):
        """Test distributed LU factorization."""
        size = 50
        ops = DistributedOperations(size=size, n_workers=2, seed=42)
        
        try:
            ops.setup_cluster()
            
            A = ops.generate_positive_definite()
            L, U = ops.lu_factorization_distributed(A)
            
            # Check shapes
            assert L.shape == (size, size), "L shape incorrect"
            assert U.shape == (size, size), "U shape incorrect"
            
            # Check reconstruction
            A_reconstructed = L @ U
            assert np.allclose(A, A_reconstructed, rtol=1e-4), \
                "Distributed LU reconstruction failed"
        
        finally:
            ops.shutdown_cluster()


class TestUtilities:
    """Test utility functions."""
    
    def test_get_memory_usage(self):
        """Test memory monitoring."""
        mem = get_memory_usage()
        assert mem > 0, "Memory usage should be positive"
        assert mem < 100000, "Memory usage seems unrealistic (>100GB)"
    
    def test_get_cpu_percent(self):
        """Test CPU monitoring."""
        cpu = get_cpu_percent(interval=0.1)
        assert cpu >= 0, "CPU percent should be non-negative"
        assert cpu <= 100, "CPU percent should not exceed 100%"


def test_imports():
    """Test that all required packages can be imported."""
    import numpy
    import dask
    import distributed
    import psutil
    import matplotlib
    import pandas
    import scipy


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
