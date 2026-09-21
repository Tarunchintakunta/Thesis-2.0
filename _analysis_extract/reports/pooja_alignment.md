# Pooja alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `pooja-thesis/Pooja_25120921_CA2.docx`  
**Alignment to formal CA2:** **~67/100** (was ~62 after GCT-v1 pass; ~48 after proxy rescore; ~85 was vs superseded NimbusGuard)

## Compact
`RQ8 Obj8 Method6 Impl10 Exp6 Metrics9 Evidence8 Claims8 Rubric4` → **~67/100**

## Formal extract (binding)
| Field | Formal CA2 |
|-------|------------|
| RQ | PAKS predictive forecasting + adaptive K8s scaling vs reactive HPA |
| Data | Google / Alibaba cluster traces |
| Method | LSTM/TF predictor; K8s API scaler; **AWS EC2 + S3 + CloudWatch** |
| Metrics | MAE/RMSE; util/efficiency; latency/throughput; **cost**; SLA/availability |
| Gantt | **MISSING** (week-grid text only — note; not primary blocker) |

## Artefact vs formal (this pass)
| Item | Status |
|------|--------|
| Binding baseline = HPA (not NimbusGuard) | Docs/code labelled; proxy quarantined (`src/proxy/`) |
| GCT/Alibaba | **GCT v1** + **GCT 2011 part-00000** (SHA256) + **Alibaba v2018 64 MiB RANGE** (SHA256). Full 2011 cell / 2019 / full Alibaba dump still open (`DATA_GAPS.md`) |
| LSTM / TF | NumPy LSTM TRACE MAE/RMSE on GCT 2011 jobs + Alibaba sample; `--backend tensorflow` fail-closed |
| K8s API scaler | Dry-run `PATCH .../scale?dryRun=All` vs HPA v2 — **not** live apply. kind/minikube **unavailable** (`results/K8S_LOCAL_PROBE.md`) |
| Formal metric columns | Wired; MAE/RMSE TRACE; util/mem/latency/cost/SLA **SIMULATED**; `live_k8s=false` |
| AWS EC2/S3/CloudWatch | **Not deployed** |

## True blockers to 100% (vs formal)
1. Full GCT 2011/2019 and/or full Alibaba dumps (samples ≠ those complete dumps) + stronger LSTM vs persistence
2. Live K8s adaptive scaling (kind/minikube or AWS) beyond dry-run JSON
3. AWS EC2/S3/CloudWatch experimental environment
4. Soft: Gantt figure; TF runtime on supported CPython if resources table is strict

**AWS required:** **yes** (method) — **not deployed** this pass; **not sole residual**
