"""
Benchmarking Module

Comprehensive benchmarking harness for comparing multi-threaded vs distributed matrix operations.
Collects metrics: completion time, peak memory, CPU utilization.
"""

import time
import json
import csv
import numpy as np
import psutil
import os
from typing import Dict, List, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
from pathlib import Path

from matrix_operations import (
    MultiThreadedOperations,
    MultiProcessOperations,
    DistributedOperations,
    get_memory_usage,
    get_cpu_percent
)


@dataclass
class BenchmarkResult:
    """Store results from a single benchmark run."""
    config_name: str
    matrix_size: int
    n_workers: int
    operation: str  # 'matmul' or 'lu'
    parallelism_model: str  # 'threaded', 'multiprocess', or 'distributed'
    completion_time: float  # seconds
    peak_memory: float  # MB
    avg_cpu_util: float  # percentage
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MemoryMonitor:
    """Monitor memory usage during benchmark execution."""
    
    def __init__(self, interval: float = 0.05):
        self.interval = interval
        self.peak_memory = 0
        self.monitoring = False
        self.thread = None
    
    def start(self):
        """Start monitoring memory."""
        self.peak_memory = 0
        self.monitoring = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self) -> float:
        """Stop monitoring and return peak memory in MB."""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=1.0)
        return self.peak_memory
    
    def _monitor(self):
        """Internal monitoring loop."""
        process = psutil.Process(os.getpid())
        while self.monitoring:
            try:
                mem = process.memory_info().rss / 1024 / 1024  # Convert to MB
                self.peak_memory = max(self.peak_memory, mem)
                time.sleep(self.interval)
            except:
                break


class CPUMonitor:
    """Monitor CPU utilization during benchmark execution."""
    
    def __init__(self, interval: float = 0.1):
        self.interval = interval
        self.cpu_samples = []
        self.monitoring = False
        self.thread = None
    
    def start(self):
        """Start monitoring CPU."""
        self.cpu_samples = []
        self.monitoring = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self) -> float:
        """Stop monitoring and return average CPU utilization."""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=1.0)
        return np.mean(self.cpu_samples) if self.cpu_samples else 0.0
    
    def _monitor(self):
        """Internal monitoring loop."""
        while self.monitoring:
            try:
                cpu = psutil.cpu_percent(interval=self.interval, percpu=False)
                self.cpu_samples.append(cpu)
            except:
                break


class BenchmarkHarness:
    """Main benchmarking harness for running and collecting results."""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[BenchmarkResult] = []
    
    def run_single_benchmark(
        self,
        operation_func: Callable,
        config_name: str,
        matrix_size: int,
        n_workers: int,
        operation: str,
        parallelism_model: str,
        *args
    ) -> BenchmarkResult:
        """
        Run a single benchmark and collect metrics.
        
        Args:
            operation_func: Function to benchmark
            config_name: Human-readable config name
            matrix_size: Size of matrix
            n_workers: Number of workers/threads/processes
            operation: Type of operation ('matmul' or 'lu')
            parallelism_model: Model used
            *args: Arguments to pass to operation_func
            
        Returns:
            BenchmarkResult with collected metrics
        """
        # Start monitors
        mem_monitor = MemoryMonitor()
        cpu_monitor = CPUMonitor()
        
        mem_monitor.start()
        cpu_monitor.start()
        
        # Run the operation
        start_time = time.perf_counter()
        try:
            result = operation_func(*args)
        except Exception as e:
            print(f"Error in {config_name}: {e}")
            raise
        end_time = time.perf_counter()
        
        # Stop monitors
        peak_memory = mem_monitor.stop()
        avg_cpu = cpu_monitor.stop()
        
        completion_time = end_time - start_time
        
        return BenchmarkResult(
            config_name=config_name,
            matrix_size=matrix_size,
            n_workers=n_workers,
            operation=operation,
            parallelism_model=parallelism_model,
            completion_time=completion_time,
            peak_memory=peak_memory,
            avg_cpu_util=avg_cpu,
            timestamp=datetime.now().isoformat()
        )
    
    def run_repeated_benchmark(
        self,
        operation_func: Callable,
        config_name: str,
        matrix_size: int,
        n_workers: int,
        operation: str,
        parallelism_model: str,
        n_iterations: int = 5,
        *args
    ) -> Dict[str, Any]:
        """
        Run benchmark multiple times and compute statistics.
        
        Returns:
            Dictionary with mean, std, and all results
        """
        results = []
        
        print(f"  Running {config_name} with {n_workers} workers, "
              f"matrix size {matrix_size}x{matrix_size} ({n_iterations} iterations)...")
        
        for i in range(n_iterations):
            result = self.run_single_benchmark(
                operation_func, config_name, matrix_size, n_workers,
                operation, parallelism_model, *args
            )
            results.append(result)
            self.results.append(result)
            print(f"    Iteration {i+1}/{n_iterations}: {result.completion_time:.3f}s")
        
        # Compute statistics
        times = [r.completion_time for r in results]
        memories = [r.peak_memory for r in results]
        cpus = [r.avg_cpu_util for r in results]
        
        return {
            'config_name': config_name,
            'matrix_size': matrix_size,
            'n_workers': n_workers,
            'operation': operation,
            'parallelism_model': parallelism_model,
            'mean_time': np.mean(times),
            'std_time': np.std(times),
            'mean_memory': np.mean(memories),
            'std_memory': np.std(memories),
            'mean_cpu': np.mean(cpus),
            'std_cpu': np.std(cpus),
            'all_times': times,
            'n_iterations': n_iterations
        }
    
    def save_results_json(self, filename: str = "benchmark_results.json"):
        """Save all results to JSON file."""
        filepath = self.output_dir / "data" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)
        
        print(f"Results saved to {filepath}")
    
    def save_results_csv(self, filename: str = "benchmark_results.csv"):
        """Save all results to CSV file."""
        filepath = self.output_dir / "data" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.results:
            return
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].to_dict().keys())
            writer.writeheader()
            for result in self.results:
                writer.writerow(result.to_dict())
        
        print(f"Results saved to {filepath}")
    
    def save_summary_statistics(self, stats: List[Dict], 
                                filename: str = "summary_statistics.json"):
        """Save summary statistics to JSON."""
        filepath = self.output_dir / "data" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"Summary statistics saved to {filepath}")


def run_full_benchmark_suite(
    matrix_sizes: List[int] = [200, 500, 1000, 1500, 2000],
    worker_counts: List[int] = [1, 2, 4, 8],
    n_iterations: int = 5,
    output_dir: str = "results"
) -> BenchmarkHarness:
    """
    Run complete benchmark suite comparing all configurations.
    
    Args:
        matrix_sizes: List of matrix dimensions to test
        worker_counts: List of worker/thread counts
        n_iterations: Number of repetitions per configuration
        output_dir: Directory for results
        
    Returns:
        BenchmarkHarness with all results
    """
    harness = BenchmarkHarness(output_dir)
    summary_stats = []
    
    print("=" * 70)
    print("MATRIX SCALING BENCHMARK SUITE")
    print("=" * 70)
    print(f"Matrix sizes: {matrix_sizes}")
    print(f"Worker counts: {worker_counts}")
    print(f"Iterations per config: {n_iterations}")
    print("=" * 70)
    
    for size in matrix_sizes:
        print(f"\n{'=' * 70}")
        print(f"Matrix Size: {size}x{size}")
        print(f"{'=' * 70}")
        
        # Generate test matrices once per size
        np.random.seed(42)
        A = np.random.rand(size, size)
        B = np.random.rand(size, size)
        A_pd = A @ A.T + np.eye(size) * size  # Positive definite for LU
        
        for n_workers in worker_counts:
            print(f"\n--- Configuration: {n_workers} worker(s) ---")
            
            # Multi-threaded matrix multiplication
            ops = MultiThreadedOperations(size, n_workers)
            stats = harness.run_repeated_benchmark(
                ops.matrix_multiply_threaded,
                f"Threaded-MatMul-{n_workers}",
                size, n_workers, "matmul", "threaded",
                n_iterations, A, B
            )
            summary_stats.append(stats)
            
            # Multi-threaded LU factorization
            stats = harness.run_repeated_benchmark(
                ops.lu_factorization_threaded,
                f"Threaded-LU-{n_workers}",
                size, n_workers, "lu", "threaded",
                n_iterations, A_pd
            )
            summary_stats.append(stats)
            
            # Multi-process matrix multiplication
            mp_ops = MultiProcessOperations(size, n_workers)
            stats = harness.run_repeated_benchmark(
                mp_ops.matrix_multiply_multiprocess,
                f"MultiProcess-MatMul-{n_workers}",
                size, n_workers, "matmul", "multiprocess",
                n_iterations, A, B
            )
            summary_stats.append(stats)
            
            # Distributed operations (only for 2+ workers)
            if n_workers >= 2:
                dist_ops = DistributedOperations(size, n_workers)
                try:
                    dist_ops.setup_cluster()
                    
                    # Distributed matrix multiplication
                    stats = harness.run_repeated_benchmark(
                        dist_ops.matrix_multiply_distributed,
                        f"Distributed-MatMul-{n_workers}",
                        size, n_workers, "matmul", "distributed",
                        n_iterations, A, B
                    )
                    summary_stats.append(stats)
                    
                    # Distributed LU factorization
                    stats = harness.run_repeated_benchmark(
                        dist_ops.lu_factorization_distributed,
                        f"Distributed-LU-{n_workers}",
                        size, n_workers, "lu", "distributed",
                        n_iterations, A_pd
                    )
                    summary_stats.append(stats)
                    
                except Exception as e:
                    print(f"Warning: Distributed operations failed: {e}")
                    print("Continuing with remaining benchmarks...")
                finally:
                    try:
                        dist_ops.shutdown_cluster()
                    except:
                        pass
    
    # Save all results
    print(f"\n{'=' * 70}")
    print("Saving results...")
    harness.save_results_json()
    harness.save_results_csv()
    harness.save_summary_statistics(summary_stats)
    print("=" * 70)
    
    return harness
