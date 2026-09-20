## Alignment note (2026-09-20)

CA2 matched-vCPU **AWS EC2** round-1 collected: `distributed-matrix-scaling/results/live/ec2_round1_summary.json`. Topology (experiment design): **1× t3.small** scale-up vs **2× t3.micro** scale-out (matched aggregate 2 vCPU; Terraform defaults). Scale-up numpy matmul n=500 ≈ **0.0067 s**; on-node Dask LocalCluster per micro ≈ **0.52 s** mean. Multi-instance Dask: 2 workers registered + futures smoke OK; `da.matmul` **timed out** (no completed multi-instance matmul cell). Local campaign remains in `results/data/`. Alignment **< 100%** until multi-instance matmul completes and eval is fully synced.

---
# Project Status: Venkat Bora - Matrix Scaling Workloads

**Student:** Sri Venkat Bora (25164414)  
**Project:** Analyzing Performance of Multi-Threaded and Distributed Matrix Scaling Workloads on Cloud Infrastructure

## Execution Environment

### Live EC2 (round-1) + local campaign

- **Live topology:** matched 2-vCPU crossover — `1× t3.small` (scale-up) vs `2× t3.micro` (scale-out); see `terraform/variables.tf` defaults.
- **Region:** `eu-west-1`; instances destroyed after round-1 (no lingering fleet).
- **Artifacts:** `distributed-matrix-scaling/results/live/ec2_round1_summary.json`.
- **Round-1 outcomes (evidence only):**
  - Scale-up numpy matmul n=500: **0.006709 s**
  - Scale-out on-node Dask LocalCluster (per micro, n=500, 1 worker): **0.5339 s** / **0.5166 s** (mean **0.5252 s**)
  - Multi-instance: scheduler + 2 workers registered; `Client.submit` futures smoke OK (`[0,1,4,9]`); **`da.matmul` status = `timed_out`** — not a completed timing cell
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
- Terraform matched-vCPU stack (`t3.small` / `t3.micro` × 2); round-1 applied then destroyed
- CLI exposes `--scheduler-address` for remote/EC2 Dask arm (`src/main.py`)

✅ **Baseline Reference:**
- Sabir & Alebrahim (2025), DOI: 10.3390/math13020298
- Extended their multi-threaded LU approach with Dask comparison

⚠️ **What's Missing / Residual:**
- **Multi-instance `da.matmul` did not complete** in round-1 (timed out after futures smoke)
- Evaluation chapter still primarily narrates local JSON; live round-1 cells need full sync
- No multi-round EC2 campaign (round-1 only)
- Inferential stats code / WhatsApp DOI `note = {doi: ...}` hygiene as previously noted

---

## AWS Deployment Path (Round-1 partial)

CA2 matched-vCPU EC2 via IaC: **round-1 executed** on `1× t3.small` vs `2× t3.micro`, then destroyed. Evidence in `results/live/ec2_round1_summary.json`.

Completed in round-1:
1. Provision matched-vCPU topology in `eu-west-1`
2. Scale-up numpy matmul (n=500) on `t3.small`
3. On-node Dask LocalCluster matmul on each `t3.micro`
4. Multi-instance scheduler + 2 workers; futures smoke

**Not completed:** multi-instance `da.matmul` wall-clock (timed out). Do **not** invent or backfill that cell. Do **not** treat local JSON times as EC2 results.

---

## Academic Integrity

- Local results are from **actual local runs**; live round-1 numbers are from **actual EC2** (`ec2_round1_summary.json`)
- Evaluation numbers for the local suite must match `summary_statistics.json` exactly
- Multi-instance matmul is reported as **timed out / partial**, not as a finished timing
- Honest about residual: completed multi-instance matmul + eval sync still outstanding

### Verified key JSON anchors (local matmul)

| Config | mean_time | Note |
|--------|-----------|------|
| Threaded 1000×1000, 1 worker | ≈67.2 ms | Baseline for speedup table |
| Threaded 1000×1000, 4 workers | ≈62.2 ms | Speedup ≈1.08× |
| Distributed 1000×1000, 4 workers | ≈344.6 ms | ≈5.54× slower than threaded-4 |
| Threaded vs Distributed through 2000 | Dist never faster | No local crossover |

### Live round-1 anchors (EC2)

| Arm | Mode | Result |
|-----|------|--------|
| 1× t3.small | numpy matmul n=500 | 0.006709 s |
| 2× t3.micro (per node) | Dask LocalCluster n=500 | mean 0.5252 s |
| Multi-instance | futures smoke | OK (2 workers) |
| Multi-instance | da.matmul n=500 | **timed_out** |

---

## Methodology Alignment

| Requirement | Status | Notes |
|------------|--------|-------|
| Baseline comparison | ✅ | Sabir & Alebrahim (2025) |
| Multi-threaded | ✅ | Threading + multiprocessing |
| Distributed (local) | ✅ | Dask LocalCluster campaign in JSON |
| Distributed (EC2 multi-instance) | ⚠️ | Workers + futures OK; `da.matmul` timed out |
| Metrics (time, memory, CPU) | ✅ | Local suite; live round-1 time cells partial |
| Matrix sizes 200-2000 | ✅ | Local; live round-1 used n=500 |
| Iterations | ⚠️ | Local committed **3**/config; live round-1 single-shot |
| Inferential stats code | ❌ | Narrative only; no Shapiro/t-test/Holm artefacts |
| Tests pass | ✅ | 20 pytest functions in tree |
| Configuration Manual | ✅ | Local setup documented |
| AWS infrastructure | ⚠️ | Round-1 applied+destroyed; residual = multi-instance matmul + eval sync |

---

**Last Updated:** 2026-09-20  
**Contact:** Sri Venkat Bora (25164414@studentmail.ncirl.ie)
