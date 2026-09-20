# Uday alignment residual (formal CA2)

**Updated:** 2026-09-20  
**Formal file:** `uday-thesis/UdayKiranReddyDodda_X25166484_proposal.docx`  
**Alignment to formal CA2:** **~18/100** (was ~90 vs superseded Et-Tousy federated proxy)

## Compact
`RQ1 Obj1 Method1 Impl3 Exp2 Metrics1 Evidence2 Claims1 Rubric2` → **~18/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | MQTT QoS 1 vs 0 loss under controlled disconnect on **AWS IoT Core** |
| Objectives | Loss; duplication+latency; reconnection/backlog; reliability–cost surface |
| Method | Device-side ID log; rules→Lambda→DynamoDB match; 16 configs × 5 reps |
| Data | **Synthetic** telemetry (allowed) |
| Baseline | Shvaika et al. (2025) |
| AWS | **Required** (IoT Core + Lambda + DynamoDB IaC) |

## Artefact vs formal
`iot-reliability/` is a **different research programme** (federated RF vs Et-Tousy OneM2M). Shared surface: “IoT” + SAM scaffold. Does **not** implement MQTT QoS, disconnection factors, or IoT Core matching.

## True blockers to 100% (vs formal)
1. Replace/repoint artefact to formal MQTT QoS disconnection experiment (or abandon formal CA2 — out of scope here)
2. Live AWS IoT Core campaign per method (synthetic devices OK)
3. Stats plan: loss/dup z-tests, latency MWU, cost surface, Holm–Bonferroni
4. Soft: retire federated-RF-as-CA2 claims in STATUS/report

**AWS required:** **yes** — **not deployed** this pass  
**Synthetic:** **not** a blocker (formal commits to synthetic)
