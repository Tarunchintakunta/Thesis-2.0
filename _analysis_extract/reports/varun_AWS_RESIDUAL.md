# Varun alignment residual (AWS-goal → sole-AWS ready)

**Updated:** 2026-09-20  
**Alignment after live lite:** **~90/100** (was ~88% after forecast-holdout hygiene)

## Compact
`RQ9 Obj12 Method12 Impl13 Exp12 Metrics11 Evidence10 Claims7 Rubric4` → **~90/100**

## Hygiene / non-AWS work done
- Fixed forecast eval: temporal holdout + no destructive `round(..., 4)` (was flat series → identical MAPEs)
- Regenerated dry-run JSON: pilot/baseline/improved all `beats_naive=true` under temporal holdout
- Abstract/conclusion/eval/design/impl demoted filler → evidence-locked tables
- STATUS demoted from SUBMIT-READY; DOI notes already present

## Live lite (2026-09-20) — measured
- Terraform apply → `s3-pred-opt-60d216643d19b67c00e7ffc8d0` (`eu-west-1`); tags: project/managed_by/purpose/data only
- S3: 48 objects (24 STANDARD + 24 STANDARD_IA @ 160 KiB); PUT mean 1008.3 / 681.6 ms; GET mean 187.2 / 524.2 ms
- CE: GetCostAndUsage AmazonS3 2026-09-13→20 sum Unblended **$3.6e-09**
- CW: ListMetrics/GetMetricStatistics ok (BucketSizeBytes empty); Logs PutLogEvents ok
- Wilcoxon n=24: cost p=9.63e-07; GET latency p=1.19e-07 (both significant)
- Modeled std−IA storage Δ: **$3.845e-05 / mo** (not CE-settled)
- Artefacts: `Varun/s3-predictive-optimization/results/live/live_lite_{summary,raw}.json`
- **Destroy complete** (8 resources)

## Sole hard residual to 100%
1. Full live S3 FinOps campaign: Inventory/metadata collector, multi-workload Wilcoxon savings protocol, CE-settled cost validation (lite probe ≠ complete CA2 AWS RQ)

**Soft / disclosed (not blockers to AWS):** ML alloc acc. 0.178; `src/metadata/` still absent.

**AWS residual:** yes (full live S3 FinOps) — **sole**

```
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=yes READY_FOR_AWS=yes LIVE_LITE=done
```
