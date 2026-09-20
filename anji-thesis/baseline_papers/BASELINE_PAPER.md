# Baseline paper (CA2-aligned)

**Student folder:** `anji-thesis`  
**Thesis:** SQS reliability/recovery under injected consumer & downstream failures  
**Selection rule:** Maximize Baseline→CA2 fit (scope / variables / method / metrics).

## Primary baseline

**Citation:** Kyrychenko, Ostapov & Kyrychenko (2025) *Optimization of SQS Configurations for Efficient Batch Data Processing* — WSEAS Trans. Systems  
**DOI:** `10.37394/23202.2025.24.4`  
**File:** `PRESENT: Kyrychenko_et_al_2025_SQS_baseline.pdf`

| Field | Baseline | Maps to thesis (CA2) |
|-------|----------|----------------------|
| **Problem** | SQS config choices affect batch throughput/latency | Same SQS service and config knobs |
| **Solution** | Empirically optimise VT, batch size, delay under healthy consumers | Extend into **failure regimes** (loss, duplicates, DLQ, recovery) |
| **Gap** | Steady-state optima; limited fault/recovery behaviour | **Their gap is your problem** |
| **Metrics** | Throughput, response time, queue length, utilisation | **Retain** throughput/latency for replication; **add** loss, duplicates, DLQ, recovery time |

**Baseline→CA2 alignment:** ~**88%**.

## Recency / relevance verdict
- **Recency:** PASS (2025). **Relevance:** HIGH (CA2-named direct SQS baseline).
