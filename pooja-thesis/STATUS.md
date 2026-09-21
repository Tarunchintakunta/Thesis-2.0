# Project Status: pooja-thesis

**Last Updated:** 2026-09-21  
**Branch:** `main`  
**Research Alignment to CA2:** **~92%** (was ~67% before live AWS k3s; formal `Pooja_25120921_CA2.docx`)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMISSION-READY / 100%)

## Summary

Formal CA2 is **PAKS**: LSTM workload prediction + adaptive Kubernetes scaling
versus **reactive HPA**, on GCT/Alibaba, on **AWS EC2/S3/CloudWatch**.

This pass closed the formal **AWS + live K8s** method gap with a Free-Tier-safe
stack: **1× t3.micro + k3s** (not EKS), **S3** results bucket, **CloudWatch**
custom metrics + log group (`project=paks-k8s-live`). Live `kubectl scale` of
`paks-demo` for HPA-formula vs PAKS-LSTM policies (12 steps, max 3 replicas);
apply-to-Ready latency recorded as **LIVE**. Stack **destroyed** after eval
(`results/aws_destroy_verify.json`).

Still open vs 100%: full GCT 2011/2019 / full Alibaba dumps (samples ≠ complete
dumps); cost still **SIMULATED** unit price; live campaign intentionally tiny;
Gantt figure / TF runtime soft.

## Evidence-bound results

### Formal — live AWS k3s (this pass)

Source: `paks-framework/results/formal_k8s_live_aws.json`,
`aws_live_run_summary.json`, `aws_destroy_verify.json`.

| Policy | live_k8s | CW metrics | Scale latency mean (s) | Evidence |
|--------|:--------:|:----------:|-----------------------:|----------|
| reactive-hpa | yes | yes | 0.349 | LIVE apply on k3s |
| paks-adaptive | yes | yes | 0.335 | LIVE apply on k3s |

`aws_deployed=true`. Instance `i-09ff2992cab1414bf` (eu-west-1) destroyed after.
Venkat `distributed-matrix-scaling` instances were **not** in this terraform
state; see destroy verify note (they were already terminated by a separate
CloudTrail event before this destroy).

### Formal — GCT 2011 jobs + Alibaba RANGE cluster (prior; seed 42)

Sources: `formal_prediction_metrics.csv`, `formal_scaling_metrics.csv`,
`RESULTS_PROVENANCE.md`.

| Series | Model | MAE | RMSE | vs persistence MAE | Evidence |
|--------|-------|----:|-----:|-------------------:|----------|
| Job windows (held-out jobs) | LSTM | 0.102 | 1.349 | persist 0.048 **lower** | TRACE (GCT 2011 part-00000) |
| Cluster CPU% (Alibaba RANGE, last 30%) | LSTM | 3.435 | 4.302 | persist 2.803 **lower** | TRACE (64 MiB sample) |

Simulated scaling loop (pre-live) remains in `formal_scaling_metrics.csv`
(`live_k8s=false` there). Prefer live JSON for K8s latency claims.

### Proxy — do not cite as formal CA2

Source: `results/results_summary.csv`. NimbusGuard-framed synthetic MLP only.

## What is done

- Formal PAKS framing; HPA as binding baseline
- GCT v1 + GCT 2011 part-00000 + Alibaba RANGE samples with SHA provenance
- NumPy LSTM; TensorFlow requested → ImportError
- Dry-run adaptive scaler vs HPA v2 **and** **live** k3s Scale apply on AWS
- Metric harness: MAE/RMSE TRACE; live scale latency LIVE; util/cost/SLA model still partly SIMULATED
- AWS EC2 + S3 + CloudWatch experimental environment (destroyed after)
- Proxy labelled (`src/proxy/`, `results/PROXY_NIMBUSGUARD.md`)

## Blockers to 100% (vs formal)

1. Full GCT 2011/2019 and/or full Alibaba dumps (samples ≠ complete dumps) — soft vs method, still residual for “complete dump” claims
2. ~~Live Kubernetes evaluation~~ **done** (tiny Free-Tier k3s; not a large multi-node stress test)
3. ~~AWS EC2 + S3 + CloudWatch~~ **done** (destroyed after)
4. Soft: Gantt figure; TF runtime; larger live campaign; billing-linked cost

## AWS

**Required (formal method):** satisfied this pass with `project=paks-k8s-live`
single-node k3s + S3 + CW, then destroyed. Residual detail:
`_analysis_extract/reports/pooja_alignment.md`.
