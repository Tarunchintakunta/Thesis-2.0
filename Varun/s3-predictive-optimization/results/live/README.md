# Live AWS results (Varun)

## Live lite (2026-09-20)

| File | Role |
|------|------|
| `live_lite_summary.json` | Measured summary: S3 PUT/GET, CE, CW, modeled storage $, Wilcoxon, destroy status |
| `live_lite_raw.json` | Paired per-object latency and modeled cost vectors ($n{=}24$) |

**Scope disclosure:** 24 objects × STANDARD vs STANDARD_IA @ 160 KiB in `eu-west-1`. Not Inventory-backed, not multi-workload, not CE-settled savings. Wilcoxon significance is for this probe only.

**Destroy:** terraform destroy complete (8 resources); bucket verified absent.

## Full evaluations e1–e3 (on main)

| Path | Role |
|------|------|
| `evaluation_r1/` … `evaluation_r3/` | `summary.json` + `raw_costs.json` per evaluation (`ca2_three_workload_wilcoxon`) |
| `BASELINE_COMPARE.md` | Human-readable Δ vs Lifecycle / IT; sig gates; high_churn little/no vs LC |
| `baseline_compare_e1_e2_e3.json` | Machine-readable aggregate + critical_analysis pos/neg |

**Protocol:** 10 trials × 80 objects × {static_archival, mixed_access, high_churn} vs Lifecycle **and** Intelligent-Tiering.  
**Gate:** `meets_ca2_two_of_three=true` for evaluations 1, 2, and 3.  
**Negative/null:** high_churn vs Lifecycle not significant (little/no improvement) — reported honestly.  
**Rebuild note:** summaries rebuilt from run logs after results-dir wipe; e1–e3 share rebuilt trial-cost vectors.
