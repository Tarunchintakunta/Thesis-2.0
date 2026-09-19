# Project Status: Venkat Bora - Matrix Scaling Workloads

**Student:** Sri Venkat Bora (25164414)  
**Project:** Analyzing Performance of Multi-Threaded and Distributed Matrix Scaling Workloads on Cloud Infrastructure

## Execution Environment

### ⚠️ LOCAL IMPLEMENTATION ONLY

This project was **completed entirely on a local development machine** using Dask local clusters, **not on AWS EC2**. The "distributed" results simulate scale-out architecture but run on a single machine with no real network overhead.

**Why local:**
- No AWS credentials required for reproduction
- Cost-free development and testing
- Academic focus on methodology demonstration

**Key limitation:** Results do not reflect true cloud network latency or multi-node distributed overhead. The "distributed" mode runs Dask workers on the same machine.

---

## Implementation Summary

✅ **What Works:**
- Multi-threaded (threading) and multi-process (multiprocessing) implementations
- Dask local cluster for simulated distributed execution
- Matrix multiplication and LU factorization
- Real benchmark data: completion time, memory (RSS), CPU utilization
- Matrix sizes 200×200 to 2000×2000, worker counts 1-8
- Statistical testing (5 runs per config, confidence intervals)
- Full test suite (pytest)
- Compiled PDF report (`latex_report/projectReport.pdf`)

✅ **Baseline Reference:**
- Sabir & Alebrahim (2025), DOI: 10.3390/math13020298
- Extended their multi-threaded LU approach with Dask comparison

⚠️ **What's Missing:**
- **No live EC2 execution** — all results are local/Dask
- No actual multi-node cluster (would show real network overhead)
- No AWS CloudWatch metrics

---

## AWS Deployment Path (Not Executed)

The code is **cloud-ready** but was not deployed. To run on AWS EC2:

1. Launch 2-3 EC2 instances (e.g., t3.xlarge) in same VPC
2. Install dependencies on each instance
3. Start Dask scheduler on one instance, workers on others
4. Run: `python src/main.py --mode distributed --scheduler-address tcp://[scheduler-ip]:8786`
5. Estimated cost: ~$1-2 for full benchmark suite

---

## Academic Integrity

- All committed results are from **actual local runs**, not fabricated
- Statistical analysis is real (t-tests, confidence intervals)
- Code is fully reproducible
- Honest about local-only execution

---

## Methodology Alignment

| Requirement | Status | Notes |
|------------|--------|-------|
| Baseline comparison | ✅ | Sabir & Alebrahim (2025) |
| Multi-threaded | ✅ | Threading + multiprocessing |
| Distributed | ⚠️ | Dask **local cluster only** |
| Metrics (time, memory, CPU) | ✅ | Real data collected |
| Matrix sizes 200-2000 | ✅ | 200, 500, 1000, 1500, 2000 |
| Statistical testing | ✅ | t-tests, 5 runs per config |
| Tests pass | ✅ | Full pytest suite |
| AWS infrastructure | ❌ | **Not executed** |

---

**Last Updated:** 2026-09-19  
**Contact:** Sri Venkat Bora (25164414@studentmail.ncirl.ie)
