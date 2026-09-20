# Final report: PAKS (formal CA2) — not submission-ready

Formal CA2 asks whether **predictive workload forecasting + adaptive Kubernetes
scaling (PAKS)** improves resource management versus **reactive HPA**, using
LSTM (TensorFlow named) on Google / Alibaba cluster traces, evaluated on a
Kubernetes cluster hosted on **AWS EC2 + S3 + CloudWatch**, with MAE/RMSE,
utilisation, response/throughput/scaling latency, cost, and SLA.

This artefact is **NOT COMPLETE**. AWS/K8s were **not** deployed this pass.

## Formal path (this pass)

- Public **Google Cluster Data v1 (2010, CC-BY)** 7-hour sample fetched and
  SHA1-verified; derived cluster/job CPU series in
  `paks-framework/data/traces/` (`PROVENANCE.md`). **Not** GCT 2011/2019 or
  Alibaba (`DATA_GAPS.md`; those loaders fail closed).
- Vanilla **LSTM** (NumPy BPTT). TensorFlow backend fail-closed on CPython 3.14.
- Adaptive scaler emits Kubernetes `apps/v1` Scale PATCH bodies with
  `dryRun=All` versus an `autoscaling/v2` HPA metrics schema.
- Metrics suite wired with TRACE vs SIMULATED tags
  (`paks-framework/results/formal_*.csv`, `RESULTS_PROVENANCE.md`).

Reproduce: `python scripts/train_lstm_and_evaluate.py --dataset gct2010`
inside `paks-framework/`.

## Proxy path (quarantined; not binding)

NimbusGuard-framed MLP + EMA/hysteresis on **synthetic** sine/spikes
(`src/proxy/`, `results/results_*.csv`). Those numbers (HPA SLA 20.0 ± 2.7,
etc.) are **artefact-as-built proxy only**. NimbusGuard is related work, not
the CA2 baseline.

## Blockers to 100%

1. GCT 2011 / 2019 and/or Alibaba (v1 slice ≠ named 2011/Alibaba dumps)
2. Live Kubernetes (kind/minikube or AWS) — dry-run JSON ≠ kubelet apply
3. AWS EC2 + S3 + CloudWatch experimental environment
4. TensorFlow runtime (optional vs NumPy LSTM) as named in the resources table
5. Soft: Gantt figure missing in formal CA2 docx

Do not mark COMPLETE.
