# Final Report: Federated QoS Offload Decisions for OneM2M IoT Middleware

## Abstract
Et-Tousy, Zyane & Sharif (2026), "Adaptive QoS Management in OneM2M Standard: Machine Learning and Deep Learning for IoT Network Optimization" (Journal of Network and Systems Management, DOI 10.1007/s10922-026-10071-4), trains a centralized Random Forest on pooled QoS telemetry to decide whether IoT traffic should stay local, partially offload, or fully offload to the cloud (98% accuracy). The paper explicitly names an unresolved gap: centralized learning "might not scale well or guarantee data privacy in distributed IoT environments," with federated learning proposed only as future work. This project reproduces the centralized baseline and builds the federated alternative the paper names but doesn't build: one Random Forest per simulated IoT site, trained on local data only, combined by averaging predicted probabilities. Across 5 seeds, federation reaches 99.5% accuracy / 99.5% macro-F1 vs. the centralized baseline's 99.9%/99.96% — recovering nearly all of the 97.6%/97.4% single-site-only lower bound — without ever pooling raw telemetry across sites.

## 1. Introduction
See `latex_report/text/introduction.tex` for the full introduction, research question, and objectives.

## 2. Literature Review Summary
(Refers to `/latex_report/text/relatedwork.tex`.) Baseline paper: Et-Tousy, J., Zyane, A., Sharif, S. (2026). *Adaptive QoS Management in OneM2M Standard: Machine Learning and Deep Learning for IoT Network Optimization.* Journal of Network and Systems Management. DOI: 10.1007/s10922-026-10071-4 (preprint: https://doi.org/10.21203/rs.3.rs-7987618/v1). Centralized RF/LightGBM ensemble for 3-class QoS-driven traffic-offload decisions (Keep Local / Partial Offload / Full Offload), 98% accuracy. States centralized learning as a named, unresolved limitation.

## 3. Methodology
Synthetic QoS telemetry for 6 non-IID simulated IoT sites (`src/data/qos_simulator.py`), each dominated by one of the paper's own traffic scenarios (uniform/burst/real-time). Labels follow the paper's exact thresholds (RTT/success-rate/CPU/RAM bands). `CentralizedRF` pools all sites' data + SMOTE (reproducing the baseline); `FederatedEnsembleRF` trains one RF per site on local data only + local SMOTE, combined via averaged predicted probabilities (the improvement); `Single-Site Local Only` evaluates one site's model in isolation as a lower bound. 5 seeds (42-46), identical RF hyperparameters across variants, evaluated on a pooled held-out test set.

## 4. Experimental Results
| Model | Accuracy | Macro-F1 | Critical Recall (class 2) |
|---|---|---|---|
| Centralized RF (baseline reproduction) | 0.9995 ± 0.0005 | 0.9996 ± 0.0005 | 0.9994 ± 0.0013 |
| Federated Ensemble RF (improved) | 0.9959 ± 0.0024 | 0.9949 ± 0.0024 | 0.9997 ± 0.0007 |
| Single-Site Local Only (no federation) | 0.9761 ± 0.0046 | 0.9737 ± 0.0051 | 0.9958 ± 0.0031 |

Raw per-seed and summary CSVs: `iot-reliability/results/results_per_seed.csv`, `results_summary.csv`. Reproduce with `python scripts/train_and_evaluate.py` inside `iot-reliability/`.

## 5. Conclusion
Federation recovers the large majority of the accuracy gap between a site going it alone (97.4% macro-F1) and full centralization (99.96%), reaching 99.49% without ever pooling raw telemetry — directly addressing the baseline paper's own stated, unresolved limitation. See `latex_report/text/conclusion.tex` for full discussion and future work (real telemetry, weighted aggregation, secure aggregation).

## Bibliography
See `latex_report/refs.bib` (`EtTousy26` entry).
