# Proxy results — NimbusGuard-framed MLP simulator

`results_summary.csv` and `results_per_seed.csv` come from
`scripts/train_and_evaluate.py` on **synthetic** cyclical load with an
`MLPRegressor`. They are **not** formal CA2 evidence.

They do **not** report MAE/RMSE on GCT/Alibaba, live util, request latency,
throughput, CloudWatch cost, or Kubernetes scaling latency.

Formal numbers: `formal_prediction_metrics.csv`, `formal_scaling_metrics.csv`,
`RESULTS_PROVENANCE.md`.
