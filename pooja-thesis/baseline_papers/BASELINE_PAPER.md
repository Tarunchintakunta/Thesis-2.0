# Baseline — Pooja (formal CA2)

**Student folder:** `pooja-thesis`  
**Binding baseline (formal CA2):** Kubernetes **Horizontal Pod Autoscaler (HPA)**
(`autoscaling/v2` CPU utilization), not NimbusGuard.

## Related literature (not the CA2 contract)

- Wanigasooriya & Ekanayake (2026) — *NimbusGuard… DQN* — IEEE ICOIN 2026  
  `doi: 10.1109/ICOIN68469.2026.11480646` / arXiv:2604.11017  
- File: `PRESENT: Wanigasooriya_Ekanayake_2026_NimbusGuard_baseline.pdf`

NimbusGuard is a proactive DQN+LSTM autoscaler vs HPA/KEDA that names an
agility–stability trade-off. The **proxy** artefact reproduced that niche with
an MLP simulator (`paks-framework/src/proxy/`). That proxy is **superseded** as
the binding story.

## Formal CA2 mapping

| Formal commitment | Artefact now | Evidence tag |
|-------------------|--------------|--------------|
| LSTM / TF on GCT or Alibaba | NumPy LSTM on **GCT v1 (2010)** public slice; TF fail-closed; 2011/2019/Alibaba absent | TRACE (v1) / GAP |
| Adaptive scaler via K8s API | Dry-run `PATCH .../scale?dryRun=All` | SIMULATED / dry-run |
| Reactive HPA comparison | HPA v2 replica formula + same dry-run schema | SIMULATED loop |
| MAE, RMSE | Job-split + cluster-split LSTM | TRACE on v1 |
| Util, latency, throughput, cost, SLA | Wired in `src/eval/metrics.py` | SIMULATED (not CloudWatch) |
| K8s on AWS EC2+S3+CloudWatch | **Not deployed** | LIVE missing |

Do **not** treat proxy `results_summary.csv` as formal HPA-vs-PAKS-on-AWS numbers.
