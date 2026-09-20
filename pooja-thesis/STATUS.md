# Project Status: pooja-thesis

**Last Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Research Alignment to CA2:** **~48%** (formal `Pooja_25120921_CA2.docx`; prior ~85% was vs superseded NimbusGuard proxy)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMISSION-READY / 100%)

## Summary

Formal CA2 commits to **PAKS** (LSTM workload prediction + adaptive K8s scaling) on **AWS EC2/S3/CloudWatch**, evaluated vs HPA with MAE/RMSE, util, latency, cost, SLA. Current artefact remains a **NimbusGuard-framed local simulator**. **Gantt figure missing** in formal docx (week grid only — note). **AWS required by formal method; not deployed this pass.**

## Evidence-bound results (seeds 42–46) — artefact as-built (simulator)

Source: `paks-framework/results/results_summary.csv` (+ `results_per_seed.csv`).

| Model | SLA Violations | Over-prov. % | Scaling Events | Pod Volatility |
|--------|---------------:|-------------:|---------------:|---------------:|
| Reactive HPA | 20.0 ± 2.7 | 40.92 ± 0.19 | 407.4 ± 4.9 | 3.32 ± 0.25 |
| Aggressive PAKS | 11.0 ± 2.2 | 45.80 ± 2.23 | 384.4 ± 9.1 | 2.86 ± 0.36 |
| Stability-Aware PAKS | 18.0 ± 2.7 | 46.52 ± 2.16 | 165.8 ± 5.3 | 1.95 ± 0.17 |

These numbers answer the **proxy** stability trade-off, not formal MAE/RMSE/cost/K8s-on-AWS eval.

## What is done
- Three policies + 5-seed driver; pytest; `CA2_COMMITMENTS.md` rewritten from formal docx

## Blockers to 100% (vs formal)
1. Trace-driven predictor (GCT/Alibaba) + MAE/RMSE
2. K8s adaptive scaling evaluation beyond simulator
3. AWS EC2/S3/CloudWatch experimental environment
4. Soft: add Gantt; retire NimbusGuard-as-binding-CA2 framing

## AWS
**Required (formal method).** Residual: `_analysis_extract/reports/pooja_alignment.md`. **Not deployed.**
