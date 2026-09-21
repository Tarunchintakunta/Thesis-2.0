# CA2 Commitments — Pooja (formal)

**Updated:** 2026-09-21  
**Branch:** `main`  
**Note:** Week-grid timeline table is present; **Gantt chart figure is MISSING** (note only — not a primary alignment blocker).  
**Status:** Binding research contract = **formal CA2**, not the prior NimbusGuard-proxy. This pass: GCT v1 + **GCT 2011 part-00000** + **Alibaba 64 MiB RANGE** + NumPy LSTM TRACE + K8s dry-run vs HPA schema; NimbusGuard MLP simulator **quarantined as PROXY**. Still **not** live K8s-on-AWS; full dumps / GCT 2019 still residual (`DATA_GAPS.md`). Alignment **~67%**. **NOT COMPLETE.**  
**AWS:** Formal method places the experimental environment on **AWS EC2 + S3 + CloudWatch** with a real Kubernetes cluster. AWS is **required for full CA2 method fidelity**. This agent pass does **not** deploy.

## Research question (formal)
Can predictive workload forecasting combined with adaptive Kubernetes scaling (PAKS) improve cloud resource management under dynamic workloads versus traditional reactive Kubernetes HPA?

## Objectives (must evidence)
1. Preprocess public cloud workload data (Google Cluster Trace / Alibaba Cluster Trace) and train a **workload prediction** model (LSTM / TensorFlow per resources table).
2. Build an adaptive scaling engine that acts on predictions via the Kubernetes API (not HPA-default alone).
3. Implement/evaluate on a **Kubernetes cluster** hosted on **AWS** (EC2 compute, S3 datasets, CloudWatch metrics; Prometheus/Grafana optional).
4. Compare PAKS vs reactive HPA across varied workload intensities (low/moderate/high/burst).

## Baseline (formal)
Traditional Kubernetes Horizontal Pod Autoscaler (HPA); literature baselines in CA2 (not NimbusGuard as the binding CA2 baseline).

## Variables / metrics
| Metric | Formal commitment |
|--------|-------------------|
| Prediction MAE, RMSE | Required |
| Resource utilisation / CPU & memory efficiency | Required |
| Response time, throughput, scaling latency | Required |
| Infrastructure cost | Required |
| SLA compliance / availability | Required |

## Non-goals / honesty
- Prior proxy “NimbusGuard EMA/hysteresis on synthetic cyclical loads only” is **superseded**.
- Local MLP simulator ≠ formal LSTM + live/controlled K8s-on-AWS testbed.
- Synthetic cyclical workloads **without** GCT/Alibaba-derived behaviour remain a gap vs formal datasets.
