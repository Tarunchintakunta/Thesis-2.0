## Alignment note (2026-09-20)

CA2 requires matched-vCPU **AWS EC2** crossover; practice is **local Dask `LocalCluster` only**. Evaluation narrative numbers must match `distributed-matrix-scaling/results/data/summary_statistics.json`. Alignment **< 100%** — AWS EC2 residual remains the hard blocker. No cloud results are claimed.

---
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

**Key limitation:** Results do not reflect true cloud network latency or multi-node distributed overhead. The "distributed" mode runs Dask workers on the same machine. **Local Dask ≠ CA2 matched-vCPU AWS EC2.**

---

## Implementation Summary

✅ **What Works:**
- Multi-threaded (threading) and multi-process (multiprocessing) implementations
- Dask local cluster for simulated distributed execution
- Matrix multiplication and LU factorization
- Real benchmark data: completion time, memory (RSS), CPU utilization
- Matrix sizes 200×200 to 2000×2000, worker counts 1–8
- Committed campaign: **90 configs × 3 iterations** (`n_iterations: 3` in JSON)
- Descriptive stats in `summary_statistics.json` (mean/std); inferential tests (t-test/Holm) **not implemented in code**
- Full test suite: **20** `test_*` functions (`test_matrix_operations.py` 11 + `test_benchmark.py` 9)
- Compiled PDF report (`latex_report/projectReport.pdf`)
- Local configuration manual: `CONFIGURATION_MANUAL.md`

✅ **Baseline Reference:**
- Sabir & Alebrahim (2025), DOI: 10.3390/math13020298
- Extended their multi-threaded LU approach with Dask comparison

⚠️ **What's Missing / Blocked:**
- **No live EC2 execution** — all results are local/Dask
- No actual multi-node cluster (would show real network overhead)
- No AWS CloudWatch metrics / IaC provision-destroy campaign
- CLI does **not** currently expose `--scheduler-address` (remote scheduler path not wired in `src/main.py`)
- WhatsApp DOI `note = {doi: ...}` format not applied in bib

---

## AWS Deployment Path (Not Executed)

CA2 proposes AWS EC2 general-purpose instances with matched aggregate vCPUs and IaC provision/destroy. That campaign **was not run**. Conceptual path (for future work only):

1. Launch matched-vCPU EC2 instances in the same VPC via IaC
2. Install dependencies on each instance
3. Start Dask scheduler on one instance, workers on others
4. Wire remote scheduler support in the CLI (not present today), then run the distributed arm against that scheduler
5. Compare against multi-threaded on a single instance with the same total vCPUs

**Do not treat any local JSON times as EC2 results.**

---

## Academic Integrity

- All committed results are from **actual local runs**, not fabricated
- Evaluation numbers must match `summary_statistics.json` exactly (absolute times, speedups, size range, `n_iterations: 3`)
- Code is reproducible locally
- Honest about local-only execution; no hallucinated AWS metrics

### Verified key JSON anchors (matmul)

| Config | mean_time | Note |
|--------|-----------|------|
| Threaded 1000×1000, 1 worker | ≈67.2 ms | Baseline for speedup table |
| Threaded 1000×1000, 4 workers | ≈62.2 ms | Speedup ≈1.08× |
| Distributed 1000×1000, 4 workers | ≈344.6 ms | ≈5.54× slower than threaded-4 |
| Threaded vs Distributed through 2000 | Dist never faster | No local crossover |

---

## Methodology Alignment

| Requirement | Status | Notes |
|------------|--------|-------|
| Baseline comparison | ✅ | Sabir & Alebrahim (2025) |
| Multi-threaded | ✅ | Threading + multiprocessing |
| Distributed | ⚠️ | Dask **local cluster only** |
| Metrics (time, memory, CPU) | ✅ | Real data collected |
| Matrix sizes 200-2000 | ✅ | 200, 500, 1000, 1500, 2000 |
| Iterations | ⚠️ | Committed **3**/config (plan text may say 5) |
| Inferential stats code | ❌ | Narrative only; no Shapiro/t-test/Holm artefacts |
| Tests pass | ✅ | 20 pytest functions in tree |
| Configuration Manual | ✅ | Local setup documented; EC2 not executed |
| AWS infrastructure | ❌ | **Not executed** (CA2 residual) |

---

**Last Updated:** 2026-09-20  
**Contact:** Sri Venkat Bora (25164414@studentmail.ncirl.ie)
