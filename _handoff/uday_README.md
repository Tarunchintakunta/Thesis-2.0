# Federated QoS Offload Decisions for OneM2M IoT Middleware

Uday's MSc Cloud Computing thesis codebase. Reproduces the classifier from
Et-Tousy, Zyane & Sharif (2026), *"Adaptive QoS Management in OneM2M
Standard: Machine Learning and Deep Learning for IoT Network Optimization"*
(Journal of Network and Systems Management, May 2026; preprint:
researchsquare.com/article/rs-7987618), and addresses a gap the paper
states explicitly in its own Discussion section.

## The baseline paper's gap
The paper trains a single, centralized Random Forest (their best model, 98%
accuracy with an ensemble) on QoS telemetry (RTT, CPU, RAM, success rate)
pooled from all IoT devices, to decide whether traffic should be kept
local, partially offloaded, or fully offloaded to the cloud. In their own
words: *"the system currently relies on a centralized learning mechanism,
which might not scale well or guarantee data privacy in distributed IoT
environments... we plan to explore federated learning."* That's future
work they name but don't build.

## What this project does
1. **Reproduces** their centralized Random Forest classifier on synthetic QoS telemetry from 6 simulated IoT edge sites, using their exact decision thresholds (RTT/success-rate/CPU/RAM bands) and their SMOTE-based class-imbalance handling.
2. **Builds the federated learning fix they named as future work**: each site trains its own Random Forest on its own local telemetry only (SMOTE-balanced locally); predictions are combined by averaging predicted probabilities across sites. No raw telemetry ever leaves the site it was generated on.
3. **Evaluates three variants** against a pooled, held-out test set: the centralized baseline, the federated ensemble, and (as a lower bound) a single site's own local model used in isolation with no federation at all.

**Result (5 seeds):** the federated ensemble closes almost all of the gap
between "go it alone" and "pool everything centrally" — see
`../final_report.md` for the numbers.

## Project Structure
- `src/data/qos_simulator.py` — synthetic QoS telemetry generator for 6 non-IID sites (each dominated by one of the paper's 3 traffic scenarios: uniform / burst / real-time).
- `src/models/qos_models.py` — `CentralizedRF` (baseline) and `FederatedEnsembleRF` (improvement).
- `scripts/train_and_evaluate.py` — trains/evaluates all 3 variants over 5 seeds, saves results, exports the deployable per-site models.
- `src/lambda_handler/app.py` — real-time inference over a Kinesis telemetry stream using the federated ensemble.
- `template.yaml` — AWS SAM template (Kinesis stream + Lambda).
- `.github/workflows/deploy.yml` (repo root) — CI: trains + deploys the SAM stack on push to `main`.

## Usage
```bash
pip install -r requirements.txt
python scripts/train_and_evaluate.py
```
Results land in `results/results_per_seed.csv` and `results/results_summary.csv`.
