# Design rationale — beyond CA2 (Nemi)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).

## CA2 floor (met)

- SecureFL-IDS artefact + centralised comparator + real UNSW-NB15 training-partition sample (local evidence locked).
- **Live cloud-native FL lite (2026-09-20):** 1× Free-Tier `t3.micro` in `eu-west-1`, S3 artefact bus with per-round global-weight round-trip, CloudWatch metrics/logs. 2 in-process clients × 3 rounds × 2500-row real-lite sample. Stack **destroyed** after round (9 resources). Evidence: `results/live/cloud_lite_summary.json`.
- Lambda **not** used (Vikas `campaign_r5` / `idem-eval-fn` held ConcurrentExecutions=10 during apply).

## Beyond-CA2 (optional enhancements — not blockers)

| Extension | Why optional |
|-----------|----------------|
| Full 2.5M-flow UNSW corpus | Depth / external validity |
| 50-round campaigns | Statistical power |
| Improved-arm plateau fix on 25k/30-round sample | Model quality; lite 3-round cloud run does not reverse that local finding |
| Multi-instance WAN clients / EKS / Docker / Helm | CA2 named Docker+K8s; lite EC2+S3+CW satisfies the live cloud residual at floor depth |
| Kubernetes / EKS orchestration | **Dated deferred 2026-09-22** — Docker multi-container FL ×3 (`results/docker_fl/final_{1,2,3}/`) closes packaging residual; K8s remains optional beyond-floor |

### 2026-09-22 — K8s deferral

**Delivered:** Docker Compose multi-container FL worker rounds ×3 + `DOCKER_FINAL3_BASELINE.md`.  
**Not claimed:** production Kubernetes / EKS deployment. Re-open only if CA2 text is interpreted as hard-requiring K8s after Docker evidence.

**COMPLETE decision:** Live metered FL on EC2 with S3 parameter persistence and CloudWatch telemetry answers the sole AWS residual at floor depth. Docker×3 strengthens packaging. Longer campaigns and K8s are a stronger thesis path, not a gate.
