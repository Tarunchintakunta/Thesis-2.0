# Project Status: pooja-thesis

**Last Updated:** 2026-09-21  
**Branch:** `main`  
**Research Alignment to CA2:** **~67%** (formal `Pooja_25120921_CA2.docx`; was ~62% after GCT-v1 pass; prior ~85% was vs superseded NimbusGuard proxy)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMISSION-READY / 100%)

## Summary

Formal CA2 is **PAKS**: LSTM workload prediction + adaptive Kubernetes scaling
versus **reactive HPA**, on GCT/Alibaba, on **AWS EC2/S3/CloudWatch**. This pass
did **not** deploy AWS/K8s. kind/minikube unavailable (Docker daemon down) —
see `paks-framework/results/K8S_LOCAL_PROBE.md`.

Non-AWS gains this pass: (1) **GCT 2011** public `task_usage` part-00000
(SHA256-verified) + job-window LSTM TRACE; (2) **Alibaba v2018** 64 MiB HTTP
RANGE sample of `machine_usage` (SHA256-verified) + cluster LSTM TRACE;
(3) scaling loop on Alibaba sample with SIMULATED util/cost/SLA; (4) formal
metric columns including `mem_util_mean`, all evidence-tagged. **Live K8s and
AWS remain open.** Full 29-day GCT 2011 / full 1.7 GiB Alibaba dump / GCT 2019
still absent. Gantt figure still missing in formal docx.

## Evidence-bound results

### Formal — GCT 2011 jobs + Alibaba RANGE cluster (seed 42)

Sources: `paks-framework/results/formal_prediction_metrics.csv`,
`formal_scaling_metrics.csv`, `RESULTS_PROVENANCE.md`, `data/traces/SAMPLE_SHA256.txt`.

| Series | Model | MAE | RMSE | vs persistence MAE | Evidence |
|--------|-------|----:|-----:|-------------------:|----------|
| Job windows (held-out jobs) | LSTM | 0.102 | 1.349 | persist 0.048 **lower** | TRACE (GCT 2011 part-00000) |
| Cluster CPU% (Alibaba RANGE, last 30%) | LSTM | 3.435 | 4.302 | persist 2.803 **lower** | TRACE (64 MiB sample) |

Job-level LSTM does **not** beat last-value persistence (many jobs near-constant).
Alibaba cluster LSTM also trails persistence on this sample. Neither is the full
29-day GCT 2011 cell nor the full Alibaba dump.

| Policy | CPU util mean | Mem util mean | SLA compliance | Cost USD (assumed) | Scaling events | Evidence |
|--------|--------------:|--------------:|---------------:|-------------------:|---------------:|----------|
| reactive-hpa | 0.701 | 0.017 | 0.980 | 44.54 | 271 | SIMULATED loop |
| paks-adaptive | 0.646 | 0.015 | 0.987 | 47.80 | 210 | SIMULATED loop; LSTM TRACE |

`live_k8s=false`. Cost/util/latency **not** CloudWatch.

### Proxy — do not cite as formal CA2 (seeds 42–46, synthetic MLP)

Source: `paks-framework/results/results_summary.csv`. NimbusGuard-framed
stability trade-off only.

## What is done (this pass)

- Formal PAKS framing; HPA as binding baseline
- GCT v1 + **GCT 2011 part-00000** + **Alibaba RANGE** samples with SHA provenance
- NumPy LSTM; TensorFlow requested → ImportError
- Dry-run adaptive scaler vs HPA v2; local kind probe documented (unavailable)
- Metric harness: MAE/RMSE, util (CPU+mem), response, throughput, scaling latency, cost, SLA
- Proxy labelled (`src/proxy/`, `results/PROXY_NIMBUSGUARD.md`)

## Blockers to 100% (vs formal)

1. Full GCT 2011/2019 and/or full Alibaba dumps (samples ≠ complete dumps)
2. Live Kubernetes evaluation (kind/minikube apply or AWS cluster) beyond dry-run
3. AWS EC2 + S3 + CloudWatch experimental environment
4. Soft: Gantt figure; TF runtime on a supported Python if the resources table is read strictly

## AWS

**Required (formal method).** Residual: `_analysis_extract/reports/pooja_alignment.md`. **Not deployed. Not sole residual.**
