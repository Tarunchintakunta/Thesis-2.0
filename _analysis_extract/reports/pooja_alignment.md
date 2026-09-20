# Pooja alignment residual (formal CA2)

**Updated:** 2026-09-20  
**Formal file:** `pooja-thesis/Pooja_25120921_CA2.docx`  
**Alignment to formal CA2:** **~48/100** (was ~85 vs superseded NimbusGuard proxy)

## Compact
`RQ6 Obj5 Method4 Impl9 Exp7 Metrics4 Evidence6 Claims4 Rubric3` → **~48/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | PAKS predictive forecasting + adaptive K8s scaling vs reactive HPA |
| Data | Google / Alibaba cluster traces (simulated realistic workloads) |
| Method | LSTM/TF predictor; K8s API scaler; **AWS EC2 + S3 + CloudWatch** |
| Metrics | MAE/RMSE; util/efficiency; latency/throughput; **cost**; SLA/availability |
| Gantt | **MISSING** (week-grid text only — note; not primary blocker) |

## Artefact vs formal
PAKS **name** + HPA comparison + SLA metric overlap. Artefact is NimbusGuard-framed MLP simulator (Aggressive vs Stability-Aware) on synthetic cyclical loads — missing formal LSTM, traces, K8s-on-AWS, MAE/RMSE/cost/latency suite.

## True blockers to 100% (vs formal)
1. Workload model + datasets per CA2 (GCT/Alibaba → MAE/RMSE), not NimbusGuard-only metrics
2. K8s adaptive scaling evaluation (not simulator-only)
3. AWS EC2/S3/CloudWatch experimental environment (formal method)
4. Soft: Gantt figure absent; retire NimbusGuard-as-binding-CA2 framing

**AWS required:** **yes** (method) — **not deployed** this pass; not sole residual while method/metrics gaps remain
