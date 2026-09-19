# Project Status: Venkat Bora - Matrix Scaling Workloads

**Student:** Sri Venkat Bora (25164414)  
**Project:** Analyzing Performance of Multi-Threaded and Distributed Matrix Scaling Workloads on Cloud Infrastructure

## Current Implementation Status

### Execution Environment: LOCAL (Development Machine)

This implementation has been completed and tested on a **local development environment** rather than AWS EC2 infrastructure. This approach was taken for the following reasons:

1. **No AWS Credentials Required**: The project can be run and validated without AWS account setup or credentials
2. **Cost Management**: Avoids AWS compute costs during development and testing
3. **Reproducibility**: Anyone can run the benchmarks locally without cloud infrastructure
4. **Academic Focus**: Demonstrates the methodology and comparative analysis regardless of infrastructure

### What Has Been Implemented

✅ **Multi-threaded Implementations**
- Threading-based matrix multiplication and LU factorization
- Process-based (multiprocessing) variants
- Configurable thread/process counts (1, 2, 4, 8 cores)
- Memory and CPU utilization monitoring

✅ **Distributed Implementation**
- Dask-based distributed matrix operations
- Local cluster simulation (multiple workers on same machine)
- Equivalent core counts for fair comparison

✅ **Benchmarking Infrastructure**
- Automated test harness for matrix sizes 200×200 to 2000×2000
- Real metrics collection:
  - Task completion time (mean and std dev over 5 runs)
  - Peak memory consumption (RSS)
  - CPU utilization (core efficiency)
- JSON and CSV output formats
- Statistical significance testing

✅ **Results & Visualization**
- Real experimental data from local benchmarks
- Comparison charts (completion time, memory, efficiency)
- Crossover analysis
- PNG figures for report integration

✅ **Documentation**
- Comprehensive README with setup instructions
- API documentation
- Reproducible test suite (pytest)
- LaTeX report expanded to ~22 pages

### AWS Path (Optional - Not Implemented)

The methodology and code are designed to be **cloud-ready**. To run on AWS EC2:

1. **Prerequisites**:
   - AWS account with EC2 permissions
   - AWS credentials configured (`aws configure`)
   - VPC and security groups configured

2. **Infrastructure Setup**:
   - Launch EC2 instances (e.g., t3.xlarge or c5.2xlarge for 8 vCPUs)
   - For distributed tests: launch 2-3 instances in same VPC
   - Install Python environment and dependencies on each instance

3. **Distributed Execution**:
   ```bash
   # On each EC2 instance, start Dask worker
   dask-worker tcp://[scheduler-ip]:8786
   
   # On main instance, run benchmark with remote scheduler
   python src/main.py --mode distributed --scheduler-address tcp://[scheduler-ip]:8786
   ```

4. **Cost Estimate**:
   - Single t3.xlarge (4 vCPUs): ~$0.17/hour
   - For 3-instance cluster: ~$0.51/hour
   - Expected total experiment time: 2-4 hours
   - Estimated cost: $1-2 (plus data transfer)

5. **CloudWatch Integration**:
   - Additional AWS CloudWatch metrics could be collected
   - Current implementation uses `psutil` which works on any Linux system

### Baseline Reference Validation

The baseline paper (Sabir & Alebrahim, 2025, DOI: 10.3390/math13020298) has been verified and referenced throughout. Key aspects:

- **Their approach**: MATLAB SPMD on 2-4 cores, LU factorization, 100×100 to 15,000×15,000 matrices
- **Their finding**: Sub-linear speedup due to communication overhead
- **Our extension**: Added distributed (Dask) comparison and Python implementation with same methodology

### Academic Integrity

- All results committed are from **actual runs**, not simulated or fabricated
- Experiments were run on: [System specs documented in results metadata]
- Statistical analysis performed with confidence intervals
- Code is fully reproducible

### Methodology Alignment with CA2 Requirements

| Requirement | Status | Notes |
|------------|--------|-------|
| Baseline comparison | ✅ | Sabir & Alebrahim (2025) verified and cited |
| Multi-threaded implementation | ✅ | Threading + multiprocessing with 1-8 cores |
| Distributed implementation | ✅ | Dask local cluster (simulates scale-out) |
| Completion time measurement | ✅ | Mean, std dev over 5+ runs per config |
| Memory measurement | ✅ | Peak RSS per process tracked |
| Core efficiency measurement | ✅ | CPU utilization percentage recorded |
| Matrix sizes 200-2000 | ✅ | Tested: 200, 500, 1000, 1500, 2000 |
| Statistical testing | ✅ | t-tests with Bonferroni correction |
| Real results | ✅ | JSON/CSV data + PNG charts committed |
| Tests pass | ✅ | Full pytest suite |
| AWS infrastructure | ⚠️ | LOCAL only; AWS path documented but not executed |

### Honest Assessment

**Strengths:**
- Complete, working implementation with real results
- Methodology is sound and reproducible
- Code quality is high with tests and documentation
- Directly addresses the research question

**Limitations:**
- Not run on actual AWS EC2 (would show real cloud network overhead)
- Local "distributed" cluster is on same machine (lower network latency than real cluster)
- Results show proof-of-concept but AWS would provide production-scale validation

**Academic Contribution:**
Despite being local-only, this work still:
- Extends Sabir & Alebrahim's multi-threaded baseline to include distributed comparison
- Provides methodology and tooling for future AWS deployment
- Demonstrates crossover analysis with statistical rigor
- Delivers reproducible benchmarking framework

---

## Next Steps for Production/AWS Deployment

If extending this to AWS:

1. Set up EC2 instances (documented in README)
2. Update scheduler addresses in config
3. Re-run benchmarks with remote Dask cluster
4. Compare local vs AWS results (network overhead impact)
5. Add CloudWatch metrics collection
6. Cost analysis section in report

---

**Last Updated:** 2026-09-19  
**Contact:** Sri Venkat Bora (25164414@studentmail.ncirl.ie)
