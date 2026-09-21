# CA2 Commitments — Pooja (formal)

**Updated:** 2026-09-21  
**Branch:** `main`  
**Note:** Week-grid timeline table is present; **Gantt chart figure is MISSING** (note only — not a primary alignment blocker).  
**Status:** Binding research contract = **formal CA2**, not the prior NimbusGuard-proxy. This pass: GCT samples + NumPy LSTM TRACE + **live** k3s Scale vs HPA on AWS (`project=paks-k8s-live`, destroy-after) + dry-run path retained. Full dumps / GCT 2019 still residual (`DATA_GAPS.md`). Alignment **~92%**. **NOT COMPLETE.**  
**AWS:** Formal method (EC2 + S3 + CloudWatch + real Kubernetes) **satisfied** this pass with Free-Tier-safe 1× t3.micro k3s; stack destroyed after eval. See `paks-framework/results/formal_k8s_live_aws.json`.

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
- Live Free-Tier k3s campaign is intentionally small (≤12 steps, max 3 replicas); not a full multi-intensity stress suite.
- Synthetic cyclical workloads **without** GCT/Alibaba-derived behaviour remain a gap vs formal datasets when used alone.
- Cost remains assumed $/pod-hour unless billing export is wired.
