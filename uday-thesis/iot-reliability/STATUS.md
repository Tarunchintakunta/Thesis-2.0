# Project Status: uday-thesis (iot-reliability)

**Last Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Research Alignment to CA2:** **~18%** (formal `UdayKiranReddyDodda_X25166484_proposal.docx`; prior ~90% was vs superseded Et-Tousy federated proxy)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Formal CA2 is **MQTT QoS 0 vs 1 reliability under controlled disconnect on AWS IoT Core** (Lambda + DynamoDB matching; synthetic devices allowed). Current tree still implements **federated RF vs Et-Tousy** — a **different** research question. **AWS IoT Core required by formal CA2; not deployed this pass.**

## Evidence-bound results (seeds 42–46) — artefact as-built (federated RF; not formal MQTT)

Source: `results/results_summary.csv` (+ `results_per_seed.csv`).

| Model | Accuracy | Macro-F1 | Critical Recall (class 2) |
|--------|---------:|---------:|-------------------------:|
| Centralized RF (baseline) | 0.9995 ± 0.0005 | 0.9996 ± 0.0005 | 0.9994 ± 0.0013 |
| Federated Ensemble RF | 0.9959 ± 0.0024 | 0.9949 ± 0.0024 | 0.9997 ± 0.0007 |
| Single-Site Local Only | 0.9761 ± 0.0046 | 0.9737 ± 0.0051 | 0.9958 ± 0.0031 |

These numbers do **not** answer the formal MQTT/IoT Core CA2.

## What is done
- Federated RF code + seeds (proxy-era); root `CA2_COMMITMENTS.md` rewritten from formal MQTT proposal

## Blockers to 100% (vs formal)
1. Implement MQTT QoS disconnection experiment (or explicitly change CA2 — out of scope here)
2. Live AWS IoT Core + rules/Lambda/DynamoDB campaign
3. Loss/dup/latency/cost metrics + pre-registered stats plan
4. Soft: STATUS/report claims must not present federated RF as formal CA2 fulfilment

## AWS
**Required.** Residual: `_analysis_extract/reports/uday_alignment.md`. **Not deployed.** Synthetic devices: **allowed**.
