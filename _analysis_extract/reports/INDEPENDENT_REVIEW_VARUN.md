# Independent review — Varun (s3-predictive-optimization)

**Date:** 2026-09-22 (updated after r4/r5)  
**Prior STATUS claim overturned:** `CA2 100%` with three full live evaluations — **not accepted as three independent evals** for archival r1–r3.  
**Honest CA2 floor (updated):** **Improved (~88)** after fresh independent `evaluation_r4` + `evaluation_r5` (distinct raw_costs SHAs; destroy-after).

## Evidence update (2026-09-22)

| Claim | Verdict | Path / numbers |
|-------|---------|----------------|
| Fresh independent r4 | **Demonstrated** | `evaluation_r4/`: SHA `7babd39c…`; `meets_ca2_two_of_three=true` (3/3 workloads); `rebuilt_from_run_log=false` |
| Fresh independent r5 | **Demonstrated** | `evaluation_r5/`: SHA `53bec5e5…`; `meets_ca2_two_of_three=true` (3/3); distinct from r4 |
| Archival r1–r3 independence | **Still Claimed / rejected** | Identical SHA `dbc3c0f1…`; keep as history only |
| Allocation accuracy improvement | **Not supported on improved arm** | Dry-run improved alloc=0.178 |

## Floor
**Improved.** Confirmatory live cost protocol now has ≥2 independent hashes. Do not resurrect r1–r3 as independent. Remaining soft: live allocation-accuracy metric; CE-settled bills.

## RQ (CA2 `VarunGampa_RIC_CA2.txt`)
> To what extent does an integrated predictive storage-class optimisation framework … reduce Amazon S3 storage cost and improve storage-class allocation accuracy, relative to AWS-native Lifecycle Policies and Intelligent-Tiering, when evaluated in a live AWS environment?

## Artefact reality
Pipeline under `Varun/s3-predictive-optimization/` (recommendation, Prophet forecast, savings, simulator, `src/metadata/` collector, Terraform). Dry-run + live lite + evaluation packs present.

## Evidence (disk)

| Claim | Verdict | Path / numbers |
|-------|---------|----------------|
| Dry-run forecast beats naive | **Demonstrated** | `results/data/*_results.json`: pilot MAPE 0.016 vs naive 0.44; baseline 0.006; improved 0.231 — all `beats_naive=true`. Allocation acc: pilot 0.32, baseline 0.504, improved **0.178** |
| Live lite S3 | **Demonstrated** | `results/live/live_lite_summary.json`: 48 objects; PUT mean STANDARD 1008.3 ms / IA 681.6; CE sum **$3.6e-09**; Wilcoxon probe p=9.63e-07 |
| e1–e3 two-of-three vs natives | **Archival only / not independent** | Identical raw SHA; `rebuilt_from_run_log=true` — history, not confirmatory independence |
| r4–r5 independent confirmatory | **Demonstrated** | Distinct SHAs; both `meets_ca2_two_of_three=true` (3/3 workloads); destroy-after |
| Allocation accuracy improvement (RQ limb) | **Not supported on improved arm** | Live eval is cost Wilcoxon, not allocation-acc; dry-run improved alloc=0.178 |
| CE-settled production savings | **Not claimed / not demonstrated** | Trial cost model; lite CE ≠ campaign |

## Highest-value remaining (soft)
1. Optional live allocation-accuracy metric on recommendations.  
2. Keep archival r1–r3 labeled non-independent in report text.
