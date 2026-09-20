# Uday alignment residual (formal CA2)

**Updated:** 2026-09-20  
**Formal file:** `uday-thesis/UdayKiranReddyDodda_X25166484_proposal.docx`  
**Artefact:** `uday-thesis/mqtt-qos-iot-core/`  
**Alignment to formal CA2:** **~56/100** (was ~18 when the only tree was the federated-RF proxy)

## Compact
`RQ8 Obj6 Method7 Impl7 Exp4 Metrics7 Evidence3 Claims8 Rubric6` → **~56/100**

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
`mqtt-qos-iot-core/` implements the **correct** programme as a **mock harness + unapplied Terraform**. `results/mock/` is explicitly **not** IoT Core evidence. `_superseded_proxy/iot-reliability/` (federated RF) is quarantined and is **not** evidence.

## True blockers to 100% (vs formal)
1. Live AWS IoT Core campaign (synthetic devices OK); `scripts/run_live.py` blocked this pass
2. Formal scale or a declared lite fold with 5 reps on live; full 5×1000×16×5 exceeds monthly IoT message free tier
3. Holm–Bonferroni + cost surface on **live** counted operations
4. Shvaika contrast using live delivery-completeness
5. Soft: report/LaTeX body against live (or clearly mock-labelled) figures

**AWS required:** **yes** — **not deployed** this pass  
**Synthetic:** **not** a blocker (formal commits to synthetic)  
**COMPLETE:** **no**
