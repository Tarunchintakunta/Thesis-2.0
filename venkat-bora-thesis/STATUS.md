## Alignment note (2026-09-23 — honest floor + SoT)

**Honest CA2 floor ≈ 85%** — time finals + rss_size + size_ladder; anti-crossover retained. Do **not** market ALIGNMENT=100.  
`INITIAL_EVAL_PASS=yes`. Final-3 **DONE**. Authority: `_analysis_extract/reports/CA2_ALIGNMENT_SCOREBOARD.md`.  
**ONE-file SoT:** `venkat-bora-thesis/CA2_PROPOSED_VS_ARTEFACT.md`.  
**Audit:** `distributed-matrix-scaling/scripts/audit_size_ladder_root_causes.py` → expect EXIT 0 / `remediable_total=0`.

Matched Free-Tier topology: **1× t3.small** vs **2× t3.micro** (aggregate 2 vCPU), `eu-west-1`. Fleet **destroyed** after each round. Live subset ≠ full 200–2000 local ladder (**DATED_WONTFIX** `DATED_WONTFIX_FULL_LIVE_LADDER_2026-09-23.md`).

```
CA2_FLOOR=~85 ALIGNMENT=honest (no market 100)
INITIAL_EVAL_PASS=yes
FINAL3=done_3of3
RSS_SIZE_FINAL=done_3of3
SIZE_LADDER=size_ladder_ladder1 (100/250/500)
SOLE_AWS_RESIDUAL=closed_under_disclosed_scope
AUTHORITY=CA2_ALIGNMENT_SCOREBOARD.md + CA2_PROPOSED_VS_ARTEFACT.md
DESTROY_CONFIRMED=yes
MOVE=allowed_when_audit_exit_0
```

### Rubric quality notes (aim 70–100; Eval 25% + Artefact 27%)

From `distributed-matrix-scaling/results/live/FINAL3_BASELINE.md` + `RSS_FINAL3_BASELINE.md` + `SIZE_LADDER_BASELINE.md`.

- **Artefact:** matched Free-Tier **1× t3.small vs 2× t3.micro** (aggregate 2 vCPU); Dask multi-instance `da.matmul`; destroy-after each round — scale-up vs scale-out under equal vCPU budget.
- **Pos:** multi-instance matmul **ok** on final_1–3 (elapsed ≈0.248–0.252 s) and initial_eval_1 (0.274 s); RSS/CPU live ×3 (multi peak RSS ~72–74 MB); size ladder 100/250/500 all `ok`; destroy confirmed.
- **Neg / mixed retained:** Free-Tier live subset ≠ full 200–2000 (local holds full ladder); round-1 n=500 multi-instance **timed_out** historically; on-node Dask LocalCluster per micro is slower than single-node numpy scale-up (expected orchestration overhead).
- **vs distributed matrix / Dask literature:** equal-vCPU crossover shows scale-out is **not** automatically faster than scale-up for this dense matmul — **anti-crossover retained**.
- **Limitations:** no Holm across orders (soft beyond CA2); full live 200–2000 WONTFIX under disclosed scope.

---
# Project Status: Venkat Bora - Matrix Scaling Workloads

**Student:** Sri Venkat Bora (25164414)  
**Project:** Analyzing Performance of Multi-Threaded and Distributed Matrix Scaling Workloads on Cloud Infrastructure

## Execution Environment

### Live EC2 (round-1 + round-2 + finals + RSS + size ladder) + local campaign

- **Live topology:** matched 2-vCPU crossover — `1× t3.small` (scale-up) vs `2× t3.micro` (scale-out); see `terraform/variables.tf` defaults.
- **Region:** `eu-west-1`; instances destroyed after each round (no lingering fleet).
- **Artifacts:**
  - Round-1: `distributed-matrix-scaling/results/live/ec2_round1_summary.json` (multi-instance matmul **timed_out** at n=500)
  - Round-2: `distributed-matrix-scaling/results/live/ec2_round2_summary.json` (multi-instance matmul **ok** at n=250)
  - **initial_eval_1 gate:** `distributed-matrix-scaling/results/live/initial_eval_1/summary.json` (matmul **ok** 0.2737 s; destroyed)
  - **final_1–3:** time-only confirmatory (`FINAL3_BASELINE.md`)
  - **rss_size_final_1–3:** peak RSS + avg CPU (`RSS_FINAL3_BASELINE.md`)
  - **size_ladder_ladder1:** orders 100/250/500 (`SIZE_LADDER_BASELINE.md`)
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
- Configuration manual: `CONFIGURATION_MANUAL.md` (local + live EC2 path)
- Terraform matched-vCPU stack (`t3.small` / `t3.micro` × 2); campaigns applied then destroyed
- Live multi-instance Dask `da.matmul` completed (round-2 + finals + RSS + size ladder)
- Scripted remediable audit: `scripts/audit_size_ladder_root_causes.py`

✅ **Baseline Reference:**
- Sabir & Alebrahim (2025), DOI: 10.3390/math13020298
- Extended their multi-threaded LU approach with Dask comparison + matched-vCPU live scale-out

⚠️ **Soft / dated (not remediable blockers under disclosed scope):**
- Full live EC2 200–2000 six-point sweep — **DATED_WONTFIX 2026-09-23** (Free-Tier subset + local full ladder)
- Inferential stats code / Holm across orders — soft beyond CA2
- WhatsApp DOI `note = {doi: ...}` hygiene as previously noted

---

## AWS Deployment Path (closed under disclosed scope)

CA2 matched-vCPU EC2 via IaC: round-1 (partial), round-2 (matmul), finals ×3, RSS/CPU ×3, size ladder 100/250/500 — all destroy-after.

Completed:
1. Provision matched-vCPU topology in `eu-west-1`
2. Scale-up numpy matmul
3. On-node Dask LocalCluster matmul on each `t3.micro`
4. Multi-instance scheduler + 2 workers; futures smoke
5. Multi-instance `da.matmul` wall-clock + RSS/CPU + size ladder

Do **not** invent cells. Do **not** treat local JSON times as EC2 results. Do **not** market a crossover that did not occur.

---

## Academic Integrity

- Local results are from **actual local runs**; live numbers are from **actual EC2** packs under `results/live/`
- Evaluation numbers for the local suite must match `summary_statistics.json` exactly
- Multi-instance matmul is reported as **ok** in round-2 / finals / RSS / size ladder; round-1 n=500 remains timed_out evidence
- Soft residuals / WONTFIX items above are honest packaging/scope gaps, not fabricated metrics

### Verified key JSON anchors (local matmul)

| Config | mean_time | Note |
|--------|-----------|------|
| Threaded 1000×1000, 1 worker | ≈67.2 ms | Baseline for speedup table |
| Threaded 1000×1000, 4 workers | ≈62.2 ms | Speedup ≈1.08× |
| Distributed 1000×1000, 4 workers | ≈344.6 ms | ≈5.54× slower than threaded-4 |
| Threaded vs Distributed through 2000 | Dist never faster | No local crossover |

### Live anchors (EC2)

| Pack | Arm | Result |
|------|-----|--------|
| round-2 n=250 | multi da.matmul | **ok — 0.2546 s** |
| final_1–3 n=250 | multi elapsed_s | ≈0.248–0.252 s |
| rss_size_final ×3 | multi peak_rss_mb | ≈72.5–72.8 MB |
| size_ladder n=100/250/500 | multi vs scale-up | scale-up ≪ multi (**anti-crossover**) |

---

## Methodology Alignment

| Requirement | Status | Notes |
|------------|--------|-------|
| Baseline comparison | ✅ | Sabir & Alebrahim (2025) |
| Multi-threaded | ✅ | Threading + multiprocessing |
| Distributed (local) | ✅ | Dask LocalCluster campaign in JSON |
| Distributed (EC2 multi-instance) | ✅ | finals + RSS + size ladder |
| Metrics (time, memory, CPU) | ✅ | Local full; live RSS/CPU on rss + ladder packs |
| Matrix sizes 200-2000 | ⚠️ | Local full; live Free-Tier 100/250/500 (WONTFIX full live) |
| Iterations | ⚠️ | Local committed **3**/config; live single-shot / descriptive ladder |
| Inferential stats code | ❌ | Narrative only; soft beyond CA2 |
| Tests pass | ✅ | 20 pytest functions in tree |
| Configuration Manual | ✅ | Local + live documented |
| AWS infrastructure | ✅ | Destroy-after; audit EXIT 0 required for MOVE |
| ONE-file SoT | ✅ | `CA2_PROPOSED_VS_ARTEFACT.md` |

---

**Last Updated:** 2026-09-23  
**Contact:** Sri Venkat Bora (25164414@studentmail.ncirl.ie)
