# Configuration Manual — Venkat Bora (25164414)

**Artefact:** `venkat-bora-thesis/distributed-matrix-scaling/`  
**Scope:** Local Dask suite **and** live Free-Tier EC2 matched-vCPU campaigns (eu-west-1).  
**Date:** 2026-09-23.

Live evidence packs (destroy-after each): `results/live/final_{1,2,3}/`, `rss_size_final_{1,2,3}/`, `size_ladder_ladder1/`. Authority baselines: `FINAL3_BASELINE.md`, `RSS_FINAL3_BASELINE.md`, `SIZE_LADDER_BASELINE.md`.

## 1. Purpose

Install, configure, run, and verify (a) the **local** matrix-scaling harness and (b) the **live EC2** scale-up vs scale-out campaigns under Free-Tier matched aggregate 2 vCPU (`1× t3.small` vs `2× t3.micro`).

## 2. Prerequisites

- Python 3.12+
- `pip` / `venv`
- macOS or Linux
- Optional: `make`
- **Live only:** AWS CLI credentials, Terraform ≥1.5, SSM Session Manager plugin; region `eu-west-1`

## 3. Install (local)

```bash
cd venkat-bora-thesis/distributed-matrix-scaling
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# or: make install
```

## 4. Environment controls

For fair threading comparisons, pin BLAS/OpenMP internal threads:

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
```

## 5. Run tests

```bash
make test
# or: pytest tests/ -v --timeout=60
```

Expected: **20** `test_*` functions (11 + 9) under `tests/`.

## 6. Run benchmarks (local Dask)

```bash
make quick-test    # subset
make benchmark     # full local suite (long)
```

Distributed mode uses Dask **`LocalCluster` on one machine**. Local JSON is **not** a substitute for multi-instance EC2 timings; cite `results/live/` for cloud claims.

### CLI note

`src/main.py` does **not** currently expose `--scheduler-address`. Live multi-instance runs use `scripts/dist_bench.py` + SSM on Terraform-provisioned hosts.

## 7. Live EC2 campaigns (Free-Tier)

Topology (Terraform defaults): **1× t3.small** (scale-up numpy) vs **2× t3.micro** (scale-out Dask multi-instance); aggregate 2 vCPU; destroy-after.

| Script | Pack / role |
|--------|-------------|
| `scripts/run_ec2_final_{1,2,3}.sh` | Time-only finals ×3 (`final_*`) |
| `scripts/run_ec2_rss_size_final.sh` | RSS/CPU instrumented ×3 (`rss_size_final_*`) |
| `scripts/run_ec2_size_ladder.sh` | Growing orders 100/250/500 (`size_ladder_ladder1`) |

Same metrics across live packs: `elapsed_s`, `peak_rss_mb`, `avg_cpu_percent` (RSS/CPU on instrumented packs + ladder).

Destroy confirmation: each pack’s `destroy_confirmed.txt` must contain `destroy_confirmed=yes`.

### Remediable audit (binding)

```bash
cd venkat-bora-thesis/distributed-matrix-scaling
python3 scripts/audit_size_ladder_root_causes.py
# expect EXIT 0; remediable_total=0
```

## 8. Outputs

| Path | Contents |
|------|----------|
| `results/data/benchmark_results.json` / `.csv` | Local per-iteration raw metrics |
| `results/data/summary_statistics.json` | Local mean/std; **`n_iterations: 3`** |
| `results/live/final_{1,2,3}/summary.json` | Live time finals |
| `results/live/rss_size_final_{1,2,3}/summary.json` | Live RSS/CPU |
| `results/live/size_ladder_ladder1/campaign_summary.json` | Live size ladder |
| `results/live/size_ladder_ladder1/analysis/size_ladder_audit_report.{json,md}` | Scripted remediable audit |

Authoritative **local** numbers: `summary_statistics.json`. Authoritative **live** numbers: the `results/live/` packs above (not local proxies).

## 9. What is intentionally absent / dated WONTFIX

- Full live six-point order set **200–2000** on EC2 (local suite covers it; Free-Tier live subset = 100/250/500) — see `DESIGN_RATIONALE_BEYOND_CA2.md` (2026-09-22/23)
- Implemented Shapiro / t-test / Holm pipelines across orders (descriptive ladder retained)
- Fabricated crossover wins (anti-crossover retained on live + local)
- Lingering EC2 fleets (destroy-after required)

## 10. CA2 status

Cloud half of the RQ is **closed under disclosed Free-Tier scope**: time finals + RSS/CPU ×3 + size ladder lite; anti-crossover retained. One-file SoT: `venkat-bora-thesis/CA2_PROPOSED_VS_ARTEFACT.md`. Honest floor ~85 — do **not** market ALIGNMENT=100.
