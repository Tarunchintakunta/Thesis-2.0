# Design rationale — beyond CA2 (Varun)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).  
**Live AWS this pass:** **not applied.** Vikas campaign r5 is RUNNING on the shared account (`ConcurrentExecutions=10`). Fuller live FinOps is Free-Tier-safe in design but **concurrency-blocked**.

## CA2 floor (met with evidence)

| Commitment | Evidence |
|------------|----------|
| Five-module stack (recommend / forecast / savings) | Dry-run JSON `results/data/{pilot,baseline,improved}_results.json`; `beats_naive=true` on temporal holdout |
| Live AWS evaluation | Lite round measured + destroyed (`results/live/live_lite_{summary,raw}.json`) — S3 PUT/GET, CE probe, CW, Wilcoxon n=24 |
| Metadata module | `src/metadata/`: lite JSON parser **and** S3 Inventory CSV parser **and** Boto3 `ListObjectsV2` (moto-tested) |
| Wilcoxon α=0.05 | Live-lite n=24 **and** local 3-workload protocol |

## Beyond-CA2 this pass (local fuller FinOps protocol)

CA2 §3.3 asks Wilcoxon across ~10–15 trial buckets × three workloads (static/archival, mixed-access, high-churn) vs Lifecycle **and** Intelligent-Tiering, plus operational overhead.

**Executed locally** (`analysis/statistics.py` → `results/data/multi_workload_wilcoxon.json`):

| Workload | n trials | Significant cost cut vs Lifecycle | vs Intelligent-Tiering | vs both natives |
|----------|---------:|:---------------------------------:|:----------------------:|:---------------:|
| static_archival | 10 | yes (p=0.00195) | yes (p=0.00195) | **yes** |
| mixed_access | 10 | yes (p=0.00195) | yes (p=0.00195) | **yes** |
| high_churn | 10 | **no** (p=0.557) | yes (p=0.00195) | no |

`meets_ca2_two_of_three` = **true** on the simulator. High-churn vs Lifecycle is reported as **not significant** (mean Δ ≈ $6.5e-5) — not back-filled.

Mean overhead (recommend + savings compare) ≈ 0.2 ms / trial-bucket.

Why this is beyond the lite live probe: three explicit CA2 workload mixes, n=10 buckets, native baselines, overhead metric. Why it is **not** a live FinOps close: trial buckets are synthetic objects, not Inventory jobs / CE-settled bills.

## Residual (not a COMPLETE gate-forget)

Live multi-workload campaign with S3 Inventory **job** output and Cost Explorer **settled** savings, when Free Tier **and** concurrency are free. Lite live + local protocol are the floor-plus-enhancement; do not treat modeled $/mo as billed USD.

**NOT COMPLETE** until that live residual is either measured or explicitly waived in a later design note. This file does **not** promote the thesis to COMPLETE.
