# PROXY artefact (not binding CA2)

This tree documents the **superseded NimbusGuard-framed simulator**:

- `src/data/workload_simulator.py` — synthetic sine + spikes (not GCT/Alibaba)
- `src/models/scalers.py` — scikit-learn `MLPRegressor` + EMA/hysteresis
- `scripts/train_and_evaluate.py` — five-seed proxy driver
- `src/lambda_handler/` + `template.yaml` — unused Kinesis/Lambda SAM stub
- `results/results_*.csv` — proxy SLA / over-prov / events / volatility

**Binding CA2** is predictive LSTM workload forecasting + adaptive Kubernetes
scaling (PAKS) versus reactive HPA, with GCT/Alibaba traces and K8s-on-AWS
(EC2 + S3 + CloudWatch). See `../../CA2_COMMITMENTS.md`, `../../DATA_GAPS.md`,
`src/models/lstm_predictor.py`, `src/k8s/`, and `scripts/train_lstm_and_evaluate.py`.

Do **not** cite proxy CSV numbers as formal MAE/RMSE, cost, or live K8s evidence.
