# Configuration manual — Pooja PAKS (`paks-framework`)

**Date:** 2026-09-23  
**SoT:** `../CA2_PROPOSED_VS_ARTEFACT.md`  
**Audit:** `python3 scripts/audit_cost_explorer_root_causes.py` (EXIT 0 required)

## Binding baseline

Kubernetes **Horizontal Pod Autoscaler (HPA)** — reactive `autoscaling/v2` CPU utilisation.  
NimbusGuard / proxy MLP paths are **not** the CA2 contract (`../baseline_papers/BASELINE_PAPER.md`).

## Live stack (Free-Tier)

| Item | Value |
|------|-------|
| Compute | 1× `t3.micro` + **k3s** (not EKS) |
| Storage / telemetry | S3 + CloudWatch (`project=paks-k8s-live`) |
| Campaign | `results/live/final_{1,2,3}/` — steps=16; seeds 41/42/43 |
| Destroy | `aws_destroy_verify.json` → `destroy_confirmed=true` each round |

Reproduce finals (when AWS slot free):

```bash
cd pooja-thesis/paks-framework
./scripts/run_final_k3s.sh   # or scripts/run_live_aws_k8s.py path in GENAI_HANDOFF
```

## Metrics & evidence tags

| Metric | Evidence |
|--------|----------|
| Scaling latency mean / p50 | **LIVE** (`kubectl` Scale → ready) |
| MAE / RMSE vs persistence | **TRACE** (`formal_prediction_metrics.csv`) |
| Util / response / throughput / SLA | Partly capacity-model **SIMULATED** |
| Infrastructure **cost** | **LIST_PRICE** — `USD_PER_POD_HOUR = 0.04` in `src/eval/metrics.py`; live `evidence.cost=SIMULATED` |

### Cost Explorer (dated WONTFIX)

**AWS Cost Explorer / GetCostAndUsage is not configured or executed** for this thesis.  
Do **not** treat LIST_PRICE pod-hour totals as billing receipts. See `../DATED_WONTFIX_N_Pooja_2026-09-23.md`.

## Honest negatives (must stay visible)

1. **LSTM MAE worse than persistence** on GCT 2011 jobs and Alibaba RANGE slices.
2. **HPA↔PAKS mean latency ordering not monotone** across final_1–3.
3. Full multi-GB dumps / multi-node campaigns remain beyond-CA2 (`../DESIGN_RATIONALE_BEYOND_CA2.md`).

## Move gate

```bash
python3 scripts/audit_cost_explorer_root_causes.py
# remediable_total must be 0
```
