# Pooja alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `pooja-thesis/Pooja_25120921_CA2.docx`  
**Alignment to formal CA2:** **~92/100** (was ~67 before live AWS k3s; ~62 after GCT-v1; ~85 was vs superseded NimbusGuard)

## Compact
`RQ8 Obj9 Method9 Impl10 Exp9 Metrics9 Evidence9 Claims9 Rubric4` → **~92/100**

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
| K8s API scaler | **LIVE** `kubectl scale` on AWS single-node **k3s** (`formal_k8s_live_aws.json`); dry-run path retained |
| Formal metric columns | MAE/RMSE TRACE; **scaling latency LIVE** (apply→Ready); util/mem/response/cost/SLA still partly SIMULATED capacity model; `live_k8s=true`, `live_cloudwatch=true` on live JSON |
| AWS EC2/S3/CloudWatch | **Deployed + destroyed** — `project=paks-k8s-live` (1× t3.micro, S3, CW namespace `PAKS/LiveK8s`) |

## True blockers to 100% (vs formal)
1. Full GCT 2011/2019 and/or full Alibaba dumps (samples ≠ those complete dumps) + stronger LSTM vs persistence — **soft** relative to method, still blocks “complete dump” / 100% purity
2. ~~Live K8s adaptive scaling~~ **closed** (tiny Free-Tier campaign; not a large multi-intensity stress suite)
3. ~~AWS EC2/S3/CloudWatch experimental environment~~ **closed** (destroy verified for Pooja tags)
4. Soft: Gantt figure; TF runtime; billing-linked cost; larger live campaign

**AWS required:** **yes** (method) — **satisfied this pass** (destroy-after). Not sole residual anymore; dump completeness + campaign scale remain.

## Honesty notes
- Live loop capped at **12 steps / max 3 replicas** on t3.micro — SLA/util from the capacity model are **not** comparable to uncapped sim CSVs.
- Cost remains assumed $/pod-hour, not AWS Cost Explorer.
- Destroy verify: Pooja resources gone. Venkat `distributed-matrix-scaling` instances were already terminated by a **separate** CloudTrail event before this terraform destroy (not in Pooja state).
