**INITIAL_EVAL_PASS:** **yes** (live AWS k3s PAKS vs HPA)

**ONE source of truth:** `CA2_PROPOSED_VS_ARTEFACT.md` (same-metrics vs HPA; LIST_PRICE cost).  
**Scripted audit:** `paks-framework/scripts/audit_cost_explorer_root_causes.py` → EXIT 0 / remediable_total=0.  
**N-Pooja (Cost Explorer soft):** `DATED_WONTFIX_N_Pooja_2026-09-23.md`.

INITIAL_EVAL_PASS=yes
Evidence: `paks-framework/results/formal_k8s_live_aws.json`. Final-3 **DONE** (`results/live/final_{1,2,3}/` + `FINAL3_BASELINE.md`).

### Rubric quality notes (aim 70–100; Eval 25% + Artefact 27%)

From `paks-framework/results/live/FINAL3_BASELINE.md` + TRACE prediction tables.

- **Artefact:** PAKS (NumPy LSTM + adaptive scale) vs reactive **HPA** on Free-Tier **1× t3.micro + k3s** with S3/CW; destroy-after; Venkat fleet never in this state.
- **Pos (final-3):** all three rounds live-apply + `destroy_confirmed`; scale latency p50 ≈0.14 s both policies; method closed under Free-Tier.
- **Neg retained:** mean HPA↔PAKS ordering **not** monotone (PAKS faster f1/f3, HPA on f2); TRACE LSTM MAE **worse** than persistence on GCT 2011 / Alibaba RANGE slices — prediction gain not automatic.
- **vs reactive HPA baseline:** live latency parity at lite n=16 single-node — do **not** claim confirmatory superiority; cost = **LIST_PRICE** `$0.04`/pod-hour SIMULATED — **Cost Explorer dated WONTFIX** (not measured).
- **Limitations:** single-node k3s; steps=16; full multi-GB dumps scoped beyond-CA2 (`DESIGN_RATIONALE_BEYOND_CA2.md`).

# Project Status: pooja-thesis

**Last Updated:** 2026-09-23  
**Branch:** `cursor/rasool-ca2-sot-audit-9837`  
**Research Alignment to CA2:** floor complete under disclosed scope (SoT audit EXIT 0) — **not** perfect marks / not Cost Explorer–validated cost  
**Status:** **CA2 floor COMPLETE** — soft residuals (full dumps, larger live campaign, TF runtime, **Cost Explorer**, Gantt) are **explicitly scoped out** / dated WONTFIX in `DATED_WONTFIX_N_Pooja_2026-09-23.md` + `DESIGN_RATIONALE_BEYOND_CA2.md`

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
- Metric harness: MAE/RMSE TRACE; live scale latency LIVE; util/SLA model still partly SIMULATED; **cost = LIST_PRICE `$0.04`/pod-hour** (Cost Explorer WONTFIX)
- AWS EC2 + S3 + CloudWatch experimental environment (destroyed after)
- Proxy labelled (`src/proxy/`, `results/PROXY_NIMBUSGUARD.md`)
- DESIGN_RATIONALE + **DATED_WONTFIX_N_Pooja** map floor vs scoped-out Cost Explorer / dumps
- SoT `CA2_PROPOSED_VS_ARTEFACT.md` + scripted audit EXIT 0

## Soft residuals (optional beyond-CA2 — not floor blockers)

1. Remaining GCT 2011 parts / 2019 Borg cells / full Alibaba ~1.7 GiB dump (coverage only)
2. Larger multi-intensity / multi-node live campaign
3. TensorFlow runtime; **Cost Explorer / billing-linked cost** (dated WONTFIX — LIST_PRICE used); Gantt figure

## AWS

**Required (formal method):** satisfied with `project=paks-k8s-live` single-node
k3s + S3 + CW, then destroyed. Alignment:
`_analysis_extract/reports/pooja_alignment.md`. No further AWS required for floor.
