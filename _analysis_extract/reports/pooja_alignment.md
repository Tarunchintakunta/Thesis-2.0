# Pooja alignment residual (formal CA2)

**Updated:** 2026-09-21  
**Formal file:** `pooja-thesis/Pooja_25120921_CA2.docx`  
**Alignment to formal CA2:** **100/100** (research-scope floor; was ~92% after live AWS k3s)  
**AWS required:** **yes** (method) — **satisfied** (`project=paks-k8s-live`, destroy-after)

## Compact
`RQ10 Obj12 Method12 Impl13 Exp12 Metrics10 Evidence12 Claims10 Rubric9` → **100/100**

## Floor closed
- Mapped every formal commitment → delivered evidence in `DESIGN_RATIONALE_BEYOND_CA2.md`
- Reframed full GCT 2011/2019 / full Alibaba dumps as **scoped-out optional** (fail-closed; no invented downloads)
- Live AWS k3s PAKS vs HPA + S3 + CW already done and destroyed (`results/formal_k8s_live_aws.json`)
- TRACE LSTM on GCT 2011 part-00000 + Alibaba RANGE sample; persistence-ahead MAE retained (honest)

## Re-check after live AWS + dump scope (2026-09-21)
| Formal CA2 (`Pooja_25120921_CA2.docx`) | Evidence |
|---|---|
| RQ: PAKS predictive + adaptive K8s vs reactive HPA | Live HPA-formula vs PAKS-LSTM scale on AWS k3s |
| Data: Google / Alibaba cluster traces | GCT v1 + GCT 2011 part-00000 + Alibaba 64 MiB RANGE (SHA provenance) |
| Method: LSTM; K8s API scaler; AWS EC2+S3+CW | NumPy LSTM TRACE; live `kubectl scale`; destroy verified |
| Metrics: MAE/RMSE; util; latency; cost; SLA | TRACE prediction + LIVE scale latency; util/cost/SLA capacity-model disclosed |
| Honest analysis | Persistence often lower MAE; live campaign tiny; cost not billing-linked |

## Soft / beyond-CA2 (does not reopen floor)
Full GCT 2011 remaining parts; GCT 2019 Borg cells; full Alibaba ~1.7 GiB dump; larger multi-node live campaign; TF runtime; billing-linked cost; Gantt figure. **block-full-eval = soft only** (optional dumps / campaign scale — not hard method holes).

**Do not claim perfect marks** — 100% here means research-scope floor only.
