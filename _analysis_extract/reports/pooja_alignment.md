# Pooja alignment residual (formal CA2)

**Updated:** 2026-09-20  
**Formal file:** `pooja-thesis/Pooja_25120921_CA2.docx`  
**Alignment to formal CA2:** **~62/100** (was ~48 after proxy rescore; ~85 was vs superseded NimbusGuard)

## Compact
`RQ8 Obj6 Method6 Impl10 Exp6 Metrics8 Evidence7 Claims8 Rubric3` → **~62/100**

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
| GCT/Alibaba | **GCT v1 2010 public slice** TRACE (CC-BY, SHA1-verified). **2011/2019/Alibaba fail-closed** (`DATA_GAPS.md`) |
| LSTM / TF | NumPy LSTM trained; `--backend tensorflow` fail-closed (no TF on CPython 3.14) |
| K8s API scaler | Dry-run `PATCH .../scale?dryRun=All` vs HPA v2 schema — **not** live apply |
| Formal metric columns | Wired; MAE/RMSE TRACE on v1 jobs; util/latency/cost/SLA **SIMULATED** |
| AWS EC2/S3/CloudWatch | **Not deployed** |

## True blockers to 100% (vs formal)
1. GCT 2011/2019 and/or Alibaba (v1 7-hour sample ≠ those dumps) + LSTM MAE/RMSE on them
2. Live K8s adaptive scaling (kind/minikube or AWS) beyond dry-run JSON
3. AWS EC2/S3/CloudWatch experimental environment
4. Soft: Gantt figure; TF runtime on supported CPython if resources table is strict

**AWS required:** **yes** (method) — **not deployed** this pass; **not sole residual**
