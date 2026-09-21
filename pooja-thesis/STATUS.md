**INITIAL_EVAL_PASS:** **yes** (live AWS k3s PAKS vs HPA; CA2 re-check still 100%)
INITIAL_EVAL_PASS=yes
Evidence: `paks-framework/results/formal_k8s_live_aws.json`. Final-3 not started.

# Project Status: pooja-thesis

**Last Updated:** 2026-09-21  
**Branch:** `main`  
**Research Alignment to CA2:** **100%** (formal `Pooja_25120921_CA2.docx`; research-scope floor — not perfect marks)  
**Status:** **CA2 floor COMPLETE** — soft residuals (full GCT/Alibaba dumps, larger live campaign, TF runtime, billing-linked cost, Gantt figure) are **explicitly scoped out** with rationale in `DESIGN_RATIONALE_BEYOND_CA2.md`

## Summary

Formal CA2 is **PAKS**: LSTM workload prediction + adaptive Kubernetes scaling
versus **reactive HPA**, on GCT/Alibaba, on **AWS EC2/S3/CloudWatch**.

Floor evidence: GCT v1 + **GCT 2011 part-00000** + **Alibaba v2018 64 MiB RANGE**
(TRACE MAE/RMSE); NumPy LSTM (TF fail-closed); **live** `kubectl scale` HPA vs
PAKS on Free-Tier **1× t3.micro + k3s** with S3 + CloudWatch
(`project=paks-k8s-live`), then **destroyed**. Full multi-GB dumps were never
fetched and are **not** claimed — optional beyond floor only.

## Evidence-bound results

### Formal — live AWS k3s (method closed)

Source: `paks-framework/results/formal_k8s_live_aws.json`,
`aws_live_run_summary.json`, `aws_destroy_verify.json`.

| Policy | live_k8s | CW metrics | Scale latency mean (s) | Evidence |
|--------|:--------:|:----------:|-----------------------:|----------|
| reactive-hpa | yes | yes | 0.349 | LIVE apply on k3s |
| paks-adaptive | yes | yes | 0.335 | LIVE apply on k3s |

`aws_deployed=true`. Instance `i-09ff2992cab1414bf` (eu-west-1) destroyed after.
Venkat `distributed-matrix-scaling` instances were **not** in this terraform
state; see destroy verify note.

### Formal — GCT 2011 jobs + Alibaba RANGE cluster (seed 42)

Sources: `formal_prediction_metrics.csv`, `formal_scaling_metrics.csv`,
`RESULTS_PROVENANCE.md`.

| Series | Model | MAE | RMSE | vs persistence MAE | Evidence |
|--------|-------|----:|-----:|-------------------:|----------|
| Job windows (held-out jobs) | LSTM | 0.102 | 1.349 | persist 0.048 **lower** | TRACE (GCT 2011 part-00000) |
| Cluster CPU% (Alibaba RANGE, last 30%) | LSTM | 3.435 | 4.302 | persist 2.803 **lower** | TRACE (64 MiB sample) |

Simulated scaling loop (pre-live) remains in `formal_scaling_metrics.csv`
(`live_k8s=false` there). Prefer live JSON for K8s latency claims.
Persistence often beats LSTM MAE on these slices — **negative result retained**.

### Proxy — do not cite as formal CA2

Source: `results/results_summary.csv`. NimbusGuard-framed synthetic MLP only.

## What is done

- Formal PAKS framing; HPA as binding baseline
- GCT v1 + GCT 2011 part-00000 + Alibaba RANGE samples with SHA provenance
- NumPy LSTM; TensorFlow requested → ImportError (fail-closed)
- Dry-run adaptive scaler vs HPA v2 **and** **live** k3s Scale apply on AWS
- Metric harness: MAE/RMSE TRACE; live scale latency LIVE; util/cost/SLA model still partly SIMULATED
- AWS EC2 + S3 + CloudWatch experimental environment (destroyed after)
- Proxy labelled (`src/proxy/`, `results/PROXY_NIMBUSGUARD.md`)
- DESIGN_RATIONALE maps floor vs scoped-out optional dumps

## Soft residuals (optional beyond-CA2 — not floor blockers)

1. Remaining GCT 2011 parts / 2019 Borg cells / full Alibaba ~1.7 GiB dump (coverage only)
2. Larger multi-intensity / multi-node live campaign
3. TensorFlow runtime; billing-linked cost; Gantt figure

## AWS

**Required (formal method):** satisfied with `project=paks-k8s-live` single-node
k3s + S3 + CW, then destroyed. Alignment:
`_analysis_extract/reports/pooja_alignment.md`. No further AWS required for floor.
