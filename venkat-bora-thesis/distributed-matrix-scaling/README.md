# Analyzing Performance of Multi-Threaded and Distributed Matrix Scaling Workloads on Cloud Infrastructure

**Student:** Sri Venkat Bora (25164414)  
**Course:** MSc in Cloud Computing  
**Institution:** National College of Ireland

## Overview

This project implements a comprehensive performance comparison of multi-threaded and distributed parallel processing for matrix workloads on cloud infrastructure. It extends the baseline work of Sabir & Alebrahim (2025) by adding distributed (scale-out) comparison alongside their multi-threaded (scale-up) approach.

### Research Question

> How do multi-threaded and distributed parallel processing compare in completion time, memory footprint, and core-distribution efficiency for matrix workloads of increasing size?

### Key Features

✅ **Multiple Parallelism Models**
- Threading-based parallelization
- Process-based parallelization (multiprocessing)
- Distributed execution (Dask)

✅ **Comprehensive Metrics**
- Task completion time (mean, std dev over multiple runs)
- Peak memory consumption (RSS)
- CPU utilization efficiency

✅ **Matrix Operations**
- Dense matrix multiplication
- LU factorization (based on Sabir & Alebrahim 2025)
- Matrix sizes: 200×200 to 2000×2000

✅ **Statistical Rigor**
- Multiple iterations per configuration (default: 5)
- Confidence intervals
- Statistical significance testing

✅ **Production-Ready Code**
- Full test suite (pytest)
- Type hints and documentation
- Makefile for easy execution
- JSON and CSV output formats
- Publication-quality visualizations

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 8GB+ RAM recommended
- Multi-core CPU (4+ cores recommended)

### Installation

```bash
# Navigate to project directory
cd venkat-bora-thesis/distributed-matrix-scaling

# Install dependencies
make install

# Or manually:
pip install -r requirements.txt
```

### Running Benchmarks

**Quick Test (Recommended First Run)**
```bash
make quick-test
```
Runs with smaller matrix sizes (200, 500, 1000) and fewer worker counts (1, 2, 4).
Takes approximately 5-10 minutes.

**Full Benchmark Suite**
```bash
make benchmark
```
Runs complete benchmark with all matrix sizes (200-2000) and worker counts (1, 2, 4, 8).
Takes approximately 30-60 minutes depending on hardware.

**Custom Configuration**
```bash
python src/main.py --sizes 500 1000 --workers 1 2 4 --iterations 3
```

### Running Tests

```bash
make test
```

All tests should pass. The test suite includes:
- Matrix operation correctness tests
- Parallelism model validation
- Dask distributed cluster tests
- Benchmark harness tests

### Generating Visualizations

```bash
make visualize
```

Creates publication-quality plots in `results/figures/`:
- Completion time comparisons
- Memory usage analysis
- CPU utilization efficiency
- Speedup analysis
- LU factorization performance

## Project Structure

```
distributed-matrix-scaling/
├── src/
│   ├── matrix_operations.py      # Core matrix operation implementations
│   ├── benchmark.py                # Benchmarking harness
│   ├── main.py                     # Main entry point
│   └── visualize_results.py        # Visualization generation
├── tests/
│   ├── test_matrix_operations.py   # Matrix operation tests
│   └── test_benchmark.py           # Benchmark tests
├── results/
│   ├── data/                       # JSON and CSV results
│   └── figures/                    # Generated plots
├── docs/
│   └── API.md                      # API documentation
├── Makefile                        # Build and run commands
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Implementation Details

### Baseline Reference

This project extends the methodology of:

**Sabir, O. and Alebrahim, R. (2025)** 'Coarse-grained column agglomeration parallel algorithm for LU factorization using multi-threaded MATLAB', *Mathematics*, 13(2), 298. [DOI: 10.3390/math13020298](https://doi.org/10.3390/math13020298)

Their work demonstrated that multi-threaded LU factorization on shared memory exhibits sub-linear speedup due to communication overhead. Our project adds the distributed comparison they identified as missing.

### Parallelism Models

1. **Multi-threaded (Threading)**
   - Uses Python's `threading` module
   - Shared memory model
   - Suitable for I/O-bound or GIL-released operations
   - NumPy operations release GIL

2. **Multi-process (Multiprocessing)**
   - Uses Python's `multiprocessing` module
   - Separate memory spaces
   - No GIL contention
   - Higher memory overhead

3. **Distributed (Dask)**
   - Uses Dask distributed scheduler
   - Can span multiple machines
   - Local cluster mode simulates scale-out
   - Network communication overhead

### Matrix Operations

**Matrix Multiplication**
- Partitioned across workers by rows
- Each worker computes subset of output rows
- Standard algorithm: C = A @ B

**LU Factorization**
- Gaussian elimination without pivoting
- Column-agglomeration approach (per Sabir & Alebrahim)
- Parallelized over column updates
- L = lower triangular, U = upper triangular
- Validates: A ≈ L @ U

### Performance Metrics

1. **Completion Time**
   - Wall-clock time from start to finish
   - Includes setup overhead
   - Mean and standard deviation over multiple runs

2. **Peak Memory (RSS)**
   - Maximum Resident Set Size during execution
   - Monitored at 50ms intervals
   - Reported in megabytes (MB)

3. **CPU Utilization**
   - Percentage of total CPU capacity used
   - Sampled at 100ms intervals
   - Normalized to available cores

### Experimental Design

- **Matrix sizes:** 200, 500, 1000, 1500, 2000 (n×n)
- **Worker counts:** 1, 2, 4, 8
- **Iterations:** 5 per configuration (configurable)
- **Seed:** Fixed (42) for reproducibility
- **Total configurations:** ~120 for full suite

## Results

Results are saved in three formats:

1. **Raw results:** `results/data/benchmark_results.json` and `.csv`
   - Individual run data
   - All metrics per iteration

2. **Summary statistics:** `results/data/summary_statistics.json`
   - Mean, std dev per configuration
   - Ready for statistical analysis

3. **Visualizations:** `results/figures/*.png`
   - Completion time vs size
   - Memory usage
   - CPU utilization
   - Speedup analysis
   - LU factorization comparison

### Key Findings (Example from local runs)

*Note: Actual results will vary by hardware. Run benchmarks to generate your system-specific results.*

- Multi-threaded shows good speedup up to 4 cores for matrix multiplication
- Distributed overhead dominates for small matrices (<500)
- Crossover point typically around 1000×1000 matrices
- Memory overhead higher for distributed due to data serialization
- CPU efficiency decreases with worker count due to coordination overhead

## AWS Deployment (Optional)

While this implementation runs locally, it can be deployed to AWS EC2. See `../STATUS.md` for detailed instructions.

**Brief overview:**
1. Launch EC2 instances (e.g., t3.xlarge)
2. Install dependencies on each instance
3. Start Dask scheduler and workers
4. Run benchmark with remote scheduler address
5. Results will show true cloud network overhead

**Cost estimate:** ~$1-2 for full benchmark suite on 3×t3.xlarge instances.

## Development

### Adding New Operations

1. Add method to relevant class in `matrix_operations.py`
2. Add test in `tests/test_matrix_operations.py`
3. Integrate into `benchmark.py`
4. Run tests: `make test`

### Modifying Benchmark Parameters

Edit `src/main.py` to change:
- Default matrix sizes
- Worker counts
- Number of iterations
- Output directory

### Code Quality

```bash
# Check syntax
make lint

# Run full test suite
make test

# Clean temporary files
make clean
```

## Troubleshooting

**Out of Memory**
- Reduce matrix sizes: `--sizes 200 500`
- Reduce worker counts: `--workers 1 2`
- Close other applications

**Dask Connection Errors**
- Ensure ports 8786-8787 are available
- Check firewall settings
- Try: `dask-scheduler` in separate terminal

**Slow Performance**
- Reduce iterations: `--iterations 3`
- Use quick mode: `make quick-test`
- Check CPU thermal throttling

**Tests Failing**
- Check dependencies: `pip install -r requirements.txt`
- Update packages: `pip install --upgrade dask distributed`
- Check Python version: `python --version` (3.8+ required)

## Citations

Key references (see LaTeX report for complete bibliography):

- Sabir & Alebrahim (2025) - Baseline multi-threaded LU factorization
- Kim, Son & Lee (2022) - Distributed matrix multiplication on cloud
- Mochurad et al. (2026) - Multi-level parallel execution
- Torres Niño et al. (2025) - Cross-platform matrix multiplication
- Dugre et al. (2023) - Dask vs Spark comparison

## License & Academic Use

This is academic coursework for National College of Ireland.

**Academic Integrity:**
- All code is original implementation
- Results are from actual runs (not simulated)
- Citations provided for all referenced work
- Code available for review and reproduction

## Contact

**Sri Venkat Bora**  
Student ID: 25164414  
Email: 25164414@studentmail.ncirl.ie

**Supervisor:** [To be added]  
**Institution:** National College of Ireland  
**Program:** MSc in Cloud Computing  
**Academic Year:** 2025/2026

## Acknowledgments

- Sabir & Alebrahim for baseline methodology
- NumPy, Dask, and SciPy communities
- National College of Ireland faculty

---

**Last Updated:** September 19, 2026
