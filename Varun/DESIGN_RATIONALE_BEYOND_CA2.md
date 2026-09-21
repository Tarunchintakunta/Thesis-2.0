# Design rationale — beyond CA2 (Varun)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).  
**Live AWS:** lite probe + **full evaluations e1–e3** are on main (`results/live/evaluation_r{1,2,3}/`, `BASELINE_COMPARE.md`). No new AWS from this note. **GENAI_HANDOFF deferred.**

## CA2 floor (met with evidence)

| Commitment | Evidence |
|------------|----------|
| Five-module stack (recommend / forecast / savings) | Dry-run JSON `results/data/{pilot,baseline,improved}_results.json`; `beats_naive=true` on temporal holdout |
| Live AWS evaluation | Lite round + full e1–e3 three-workload Wilcoxon vs Lifecycle **and** IT; `meets_ca2_two_of_three=true` each eval |
| Metadata module | `src/metadata/`: lite JSON parser **and** S3 Inventory CSV parser **and** Boto3 `ListObjectsV2` (moto-tested) |
| Wilcoxon α=0.05 | Live-lite n=24 **and** live e1–e3 n=10/workload (high_churn vs LC null retained) |

## Live e1–e3 + local protocol (same workload pattern)

CA2 §3.3 asks Wilcoxon across ~10–15 trial buckets × three workloads (static/archival, mixed-access, high-churn) vs Lifecycle **and** Intelligent-Tiering.

**Live artefacts** (`evaluation_r{1,2,3}/`, `BASELINE_COMPARE.md`) and **local** (`results/data/multi_workload_wilcoxon.json`) share the same qualitative pattern:

| Workload | n trials | Significant cost cut vs Lifecycle | vs Intelligent-Tiering | vs both natives |
|----------|---------:|:---------------------------------:|:----------------------:|:---------------:|
| static_archival | 10 | yes (p=0.00195) | yes (p=0.00195) | **yes** |
| mixed_access | 10 | yes (p=0.00195) | yes (p=0.00195) | **yes** |
| high_churn | 10 | **no** (p=0.557) | yes (p=0.00195) | no |

`meets_ca2_two_of_three` = **true** on live e1–e3 and on the simulator. High-churn vs Lifecycle is **not significant** (mean Δ ≈ $6.5e-5) — retained honestly. e1–e3 summaries disclose rebuild-from-log identity across evaluation folders.

## Soft residuals (handoff deferred)

- Optional fresh independent sampling if stronger multi-eval independence is desired for marks.
- Do not treat trial/list-price $/mo as CE-settled bills.
- **GENAI_HANDOFF.md** not written (policy deferred).
- CA2 floor = **100%** on scoreboard; this file does not invent additional metrics.
