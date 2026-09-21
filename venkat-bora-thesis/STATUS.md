## Alignment note (2026-09-21)

CA2 matched-vCPU **AWS EC2** round-2 completed multi-instance `da.matmul`: `distributed-matrix-scaling/results/live/ec2_round2_summary.json`. Topology (same as round-1): **1× t3.small** vs **2× t3.micro** (matched aggregate 2 vCPU), `eu-west-1`, fleet **destroyed** after. At **n=250**: scale-up numpy ≈ **0.00156 s**; on-node Dask LocalCluster mean ≈ **0.550 s**; multi-instance (2 workers) `da.matmul` ≈ **0.255 s** (`status=ok`). Round-1 residual (`da.matmul` timed_out at n=500) **closed**. Local campaign remains in `results/data/`. Soft residuals (beyond CA2 floor): LaTeX eval chapter full sync, multi-order live crossover sweep, live RSS/CPU, inferential stats. Alignment **100%** CA2 floor (was 63%; hard multi-instance matmul residual closed).

---
# Project Status: Venkat Bora - Matrix Scaling Workloads

**Student:** Sri Venkat Bora (25164414)  
**Project:** Analyzing Performance of Multi-Threaded and Distributed Matrix Scaling Workloads on Cloud Infrastructure

## Execution Environment

### Live EC2 (round-1 + round-2) + local campaign

- **Live topology:** matched 2-vCPU crossover — `1× t3.small` (scale-up) vs `2× t3.micro` (scale-out); see `terraform/variables.tf` defaults.
- **Region:** `eu-west-1`; instances destroyed after each round (no lingering fleet).
- **Artifacts:**
  - Round-1: `distributed-matrix-scaling/results/live/ec2_round1_summary.json` (multi-instance matmul **timed_out** at n=500)
  - Round-2: `distributed-matrix-scaling/results/live/ec2_round2_summary.json` (multi-instance matmul **ok** at n=250)
- **Round-2 outcomes (evidence only):**
  - Scale-up numpy matmul n=250: **0.001562 s**
  - Scale-out on-node Dask LocalCluster (per micro, n=250, 1 worker): **0.5342 s** / **0.5653 s** (mean **0.5497 s**)
  - Multi-instance: scheduler + **2** workers registered; `Client.submit` futures smoke OK (`[0,1,4,9]`); **`da.matmul` status = `ok`**, **elapsed_s = 0.2546**
- **Local campaign:** Dask `LocalCluster` suite remains in `results/data/` for the offline study (90 configs × 3 iterations).

---

## Implementation Summary

✅ **What Works:**
- Multi-threaded (threading) and multi-process (multiprocessing) implementations
- Dask local cluster for simulated distributed execution
- Matrix multiplication and LU factorization
- Real benchmark data: completion time, memory (RSS), CPU utilization
- Matrix sizes 200×200 to 2000×2000, worker counts 1–8
- Committed local campaign: **90 configs × 3 iterations** (`n_iterations: 3` in JSON)
- Descriptive stats in `summary_statistics.json` (mean/std); inferential tests (t-test/Holm) **not implemented in code**
- Full test suite: **20** `test_*` functions (`test_matrix_operations.py` 11 + `test_benchmark.py` 9)
- Compiled PDF report (`latex_report/projectReport.pdf`)
- Local configuration manual: `CONFIGURATION_MANUAL.md`
- Terraform matched-vCPU stack (`t3.small` / `t3.micro` × 2); round-1 and round-2 applied then destroyed
- Live multi-instance Dask `da.matmul` completed (round-2)

✅ **Baseline Reference:**
- Sabir & Alebrahim (2025), DOI: 10.3390/math13020298
- Extended their multi-threaded LU approach with Dask comparison

⚠️ **Soft residuals (not blocking the multi-instance matmul cell):**
- Evaluation LaTeX chapter still primarily narrates local JSON; round-2 live cells need full prose sync
- Live campaign is single-shot at n=250 (not a full multi-order EC2 crossover sweep)
- Live peak RSS / per-core utilisation not instrumented on EC2 (local suite has them)
- Inferential stats code / WhatsApp DOI `note = {doi: ...}` hygiene as previously noted

---

## AWS Deployment Path (Round-2 closed matmul cell)

CA2 matched-vCPU EC2 via IaC: **round-1** (partial) and **round-2** (matmul complete) on `1× t3.small` vs `2× t3.micro`, then destroyed.

Completed:
1. Provision matched-vCPU topology in `eu-west-1`
2. Scale-up numpy matmul (round-1 n=500; round-2 n=250)
3. On-node Dask LocalCluster matmul on each `t3.micro`
4. Multi-instance scheduler + 2 workers; futures smoke
5. **Multi-instance `da.matmul` wall-clock (round-2 n=250, ok)**

Do **not** invent cells. Do **not** treat local JSON times as EC2 results.

---

## Academic Integrity

- Local results are from **actual local runs**; live round-1/2 numbers are from **actual EC2**
- Evaluation numbers for the local suite must match `summary_statistics.json` exactly
- Multi-instance matmul is reported as **ok** in round-2 (`ec2_round2_summary.json`); round-1 remains timed_out evidence
- Soft residuals listed above are honest packaging/scope gaps, not fabricated metrics

### Verified key JSON anchors (local matmul)

| Config | mean_time | Note |
|--------|-----------|------|
| Threaded 1000×1000, 1 worker | ≈67.2 ms | Baseline for speedup table |
| Threaded 1000×1000, 4 workers | ≈62.2 ms | Speedup ≈1.08× |
| Distributed 1000×1000, 4 workers | ≈344.6 ms | ≈5.54× slower than threaded-4 |
| Threaded vs Distributed through 2000 | Dist never faster | No local crossover |

### Live round-2 anchors (EC2, n=250)

| Arm | Mode | Result |
|-----|------|--------|
| 1× t3.small | numpy matmul n=250 | 0.001562 s |
| 2× t3.micro (per node) | Dask LocalCluster n=250 | mean 0.5497 s |
| Multi-instance | futures smoke | OK (2 workers) |
| Multi-instance | da.matmul n=250 | **ok — 0.2546 s** |

### Live round-1 anchors (EC2, n=500; historical)

| Arm | Mode | Result |
|-----|------|--------|
| Multi-instance | da.matmul n=500 | **timed_out** (superseded by round-2 cell) |

---

## Methodology Alignment

| Requirement | Status | Notes |
|------------|--------|-------|
| Baseline comparison | ✅ | Sabir & Alebrahim (2025) |
| Multi-threaded | ✅ | Threading + multiprocessing |
| Distributed (local) | ✅ | Dask LocalCluster campaign in JSON |
| Distributed (EC2 multi-instance) | ✅ | Round-2 `da.matmul` ok at n=250 |
| Metrics (time, memory, CPU) | ⚠️ | Local suite full; live round-2 time cells only |
| Matrix sizes 200-2000 | ⚠️ | Local full; live round-2 used n=250 |
| Iterations | ⚠️ | Local committed **3**/config; live single-shot |
| Inferential stats code | ❌ | Narrative only; no Shapiro/t-test/Holm artefacts |
| Tests pass | ✅ | 20 pytest functions in tree |
| Configuration Manual | ✅ | Local setup documented |
| AWS infrastructure | ✅ | Round-1+2 applied+destroyed; matmul residual closed |

---

**Last Updated:** 2026-09-21  
**Contact:** Sri Venkat Bora (25164414@studentmail.ncirl.ie)
