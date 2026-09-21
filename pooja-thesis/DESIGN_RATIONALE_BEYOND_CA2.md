# Design rationale — CA2 floor + scoped residuals (Pooja)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).  
**Bar:** 100% CA2 = RQ / objectives / gap / method / artefact / eval **scope** — not perfect marks.  
**AWS:** Formal method required EC2 + S3 + CloudWatch + live Kubernetes — **satisfied** (`project=paks-k8s-live`, destroy-after).

## Formal CA2 → delivered (floor met)

| Commitment | Delivered evidence | Scope note |
|------------|-------------------|------------|
| RQ: PAKS predictive forecasting + adaptive K8s scaling vs reactive HPA | Live `kubectl scale` HPA-formula vs PAKS-LSTM on AWS k3s; dry-run path retained | Tiny Free-Tier campaign (≤12 steps, max 3 replicas) — method fidelity, not stress suite |
| Obj: preprocess Google / Alibaba traces; train workload LSTM | GCT v1 + GCT 2011 `part-00000` + Alibaba v2018 **64 MiB RANGE**; NumPy LSTM TRACE MAE/RMSE | Formal CA2 names trace **families**, not full multi-GB dumps |
| Obj: adaptive scaler via Kubernetes API | LIVE apply→Ready latency in `formal_k8s_live_aws.json` | `live_k8s=true` |
| Obj: AWS EC2 + S3 + CloudWatch experimental environment | 1× t3.micro + S3 + CW namespace `PAKS/LiveK8s`; destroy verified | Not EKS; Free-Tier-safe single node |
| Metrics: MAE/RMSE; util/efficiency; latency/throughput; cost; SLA | TRACE prediction + LIVE scale latency; util/cost/SLA capacity-model | Cost = assumed $/pod-hour (not Cost Explorer) |

## Explicitly scoped out (fail-closed; still CA2-complete)

These are **optional beyond-CA2 enhancements**, not open formal-scope holes:

1. **Full GCT 2011 29-day cell** (~remaining parts after `part-00000`) — not required once a disclosed, SHA-pinned shard supports TRACE LSTM + scaling method evidence. Remaining parts raise coverage/power, not the RQ.
2. **GCT 2019 Borg cells** — formal CA2 names *Google Cluster Trace*, not “2019 eight-cell.” Optional generation upgrade.
3. **Full Alibaba v2018 `machine_usage.tar.gz` (~1.7 GiB)** — formal CA2 requires Alibaba (or GCT) family evidence; the disclosed **HTTP RANGE 64 MiB** sample already yields TRACE cluster LSTM metrics with provenance. Fetching the full dump is optional beyond floor; do **not** invent a download that was never landed.
4. **Large multi-intensity / multi-node live campaign** — soft validity upgrade; Free-Tier single-node k3s already closes the AWS+K8s method commitment.
5. **TensorFlow runtime / billing-linked cost / Gantt figure** — resources-table / packaging soft items; NumPy LSTM fail-closed TF path and assumed $/pod-hour are disclosed.

**Rationale:** inventing full-dump coverage or silently swapping synthetic workloads for TRACE claims would break evidence rules. Disclosing sample limits and retaining LSTM-vs-persistence honesty (persistence often lower MAE on these slices) meets research-scope alignment better than chasing optional multi-GB dumps.

## Beyond-CA2 already present

- GCT v1 (2010) slice alongside 2011 part + Alibaba RANGE
- Dry-run HPA v2 path + local kind/minikube probe notes
- Live CloudWatch custom metrics on Free-Tier stack (destroyed after)

## Alignment

**Formal CA2 research-scope: 100%.** Soft residuals above remain optional; they do **not** reopen the floor.
