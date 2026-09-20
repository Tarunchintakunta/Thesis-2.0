# Project Status: pooja-thesis

**Last Updated:** 2026-09-20  
**Branch:** `cursor/pooja-paks-formal-raise-58c5` (onto `feature/aws-ca2-alignment`)  
**Research Alignment to CA2:** **~62%** (formal `Pooja_25120921_CA2.docx`; was ~48% after proxy rescore; prior ~85% was vs superseded NimbusGuard proxy)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMISSION-READY / 100%)

## Summary

Formal CA2 is **PAKS**: LSTM workload prediction + adaptive Kubernetes scaling
versus **reactive HPA**, on GCT/Alibaba, on **AWS EC2/S3/CloudWatch**. This pass
did **not** deploy AWS/K8s.

Raised non-AWS residuals: (1) NimbusGuard simulator **quarantined as PROXY**;
(2) public **GCT v1 (2010)** slice + LSTM MAE/RMSE (TRACE) with fail-closed
2011/2019/Alibaba loaders; (3) dry-run K8s Scale API vs HPA v2 schema;
(4) formal metric columns with SIMULATED vs TRACE tags. **GCT 2011/Alibaba,
live K8s, and AWS remain open.** Gantt figure still missing in formal docx.

## Evidence-bound results

### Formal — GCT v1 LSTM + simulated HPA/PAKS loop (one run, seed 42)

Sources: `paks-framework/results/formal_prediction_metrics.csv`,
`formal_scaling_metrics.csv`, `RESULTS_PROVENANCE.md`.

| Series | Model | MAE | RMSE | vs persistence MAE | Evidence |
|--------|-------|----:|-----:|-------------------:|----------|
| Job windows (held-out jobs) | LSTM | 0.106 | 1.041 | persist 0.034 **lower** | TRACE (GCT v1) |
| Cluster CPU (last 30% of 75 bins) | LSTM | 16.80 | 20.64 | persist 19.95 | TRACE, **small n** |

Job-level LSTM does **not** beat last-value persistence (many jobs near-constant). Cluster n_test≈19. Not GCT 2011/Alibaba.

| Policy | CPU util mean | SLA compliance | Cost USD (assumed) | Scaling events | Evidence |
|--------|--------------:|---------------:|-------------------:|---------------:|----------|
| reactive-hpa | 1.21 | 0.987 | 13.76 | 58 | SIMULATED loop |
| paks-adaptive | 1.18 | 0.987 | 14.41 | 47 | SIMULATED loop; LSTM TRACE |

Tied SLA in this short series; cost/util/latency **not** CloudWatch. `live_k8s=false`.

### Proxy — do not cite as formal CA2 (seeds 42–46, synthetic MLP)

Source: `paks-framework/results/results_summary.csv`. NimbusGuard-framed
stability trade-off only.

| Model | SLA Violations | Over-prov. % | Scaling Events | Pod Volatility |
|--------|---------------:|-------------:|---------------:|---------------:|
| Reactive HPA | 20.0 ± 2.7 | 40.92 ± 0.19 | 407.4 ± 4.9 | 3.32 ± 0.25 |
| Aggressive PAKS | 11.0 ± 2.2 | 45.80 ± 2.23 | 384.4 ± 9.1 | 2.86 ± 0.36 |
| Stability-Aware PAKS | 18.0 ± 2.7 | 46.52 ± 2.16 | 165.8 ± 5.3 | 1.95 ± 0.17 |

## What is done (this pass)

- Formal PAKS framing; HPA as binding baseline
- GCT v1 public slice (CC-BY, SHA1-verified) + `DATA_GAPS.md` fail-closed loaders
- NumPy LSTM; TensorFlow requested → ImportError
- Dry-run adaptive scaler (`PATCH .../scale?dryRun=All`) vs HPA v2 metrics schema
- Metric harness: MAE/RMSE, util, response, throughput, scaling latency, cost, SLA
- Proxy labelled (`src/proxy/`, `results/PROXY_NIMBUSGUARD.md`)

## Blockers to 100% (vs formal)

1. GCT 2011/2019 and/or Alibaba dumps (v1 7-hour sample ≠ those traces)
2. Live Kubernetes evaluation (kind/minikube apply or AWS cluster) beyond dry-run
3. AWS EC2 + S3 + CloudWatch experimental environment
4. Soft: Gantt figure; TF runtime on a supported Python if the resources table is read strictly

## AWS

**Required (formal method).** Residual: `_analysis_extract/reports/pooja_alignment.md`. **Not deployed. Not sole residual.**
