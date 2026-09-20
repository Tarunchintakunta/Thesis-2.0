# SecureFL-IDS: Privacy-Preserving Federated Intrusion Detection

**Student:** Nemi Ishwarlal Vikani (24303046)  
**Programme:** MSc in Cloud Computing  
**Institution:** National College of Ireland

**Research Question:** What is the effect of combining Federated Learning and Differential Privacy on the accuracy, privacy preservation and overall performance of cloud-native intrusion detection systems compared with traditional systems and existing federated learning-based approaches?

## Overview

SecureFL-IDS is a privacy-preserving federated intrusion detection framework for cloud-native environments. The system enables collaborative threat detection across distributed cloud tenants without sharing sensitive network data. This artefact implements:

1. **Baseline**: Replication of the Saklani et al. (2026) PP-FL-DP-IDS approach
2. **Improved**: Enhanced version with lightweight differential privacy and communication-efficient aggregation

## Baseline Paper

Saklani, S., Chohan, D.K., and Sharma, R. (2026) 'Privacy Preserving Cloud Native Intrusion Detection Using Federated Learning and Differential Privacy', *2026 8th International Conference on Intelligent Sustainable Systems (ICISS)*, pp. 387–392. https://doi.org/10.1109/iciss67859.2026.11454085

**Baseline Paper (Saklani et al. 2026):** reports 91.8% accuracy / F1 >90% on full UNSW-NB15 — **literature reference only**, not this PoC's committed results.

## Quick Start (One Command, Local Simulation)

```bash
make pilot
```

## Full Usage

```bash
make test          # Run unit tests
make centralised   # CA2 centralised IDS comparator (synthetic) + merge
make experiment    # Federated baseline + improved (synthetic)
make unsw-real     # Real UNSW training-partition sample (central + FL)
make stats         # Generate statistical analysis
make figures       # Create evaluation figures
```

## Project Structure

```
securefl-ids/
├── src/
│   ├── baseline/         # Saklani et al. (2026) FL implementation
│   ├── centralised/      # CA2 traditional centralised IDS comparator
│   ├── improved/         # Enhanced SecureFL-IDS
│   └── common/           # Shared utilities (data, metrics, FL orchestration)
├── tests/                # Unit and integration tests
├── scripts/              # Data download, experiment runners
├── docs/                 # Configuration manual, architecture
├── results/              # Experiment outputs (metrics, logs)
│   ├── comparison/       # Synthetic PoC (incl. centralised arm)
│   └── unsw_real/        # Real training-partition sample campaign
├── terraform/            # AWS scaffold (NOT applied)
└── figures/              # Evaluation plots
```

## Key Features

### Centralised comparator (CA2 traditional baseline)
- Pooled CNN training on the same CSV path as FL arms
- No federated split / no DP; communication cost reported as 0.0 (N/A)

### Baseline (Saklani et al. 2026)
- Federated Learning with FedAvg aggregation
- Differential Privacy (ε=1.0, δ=1e-5) via gradient clipping + Gaussian noise
- CNN-based binary intrusion classifier
- Non-IID data distribution across clients

### Improved (SecureFL-IDS)
- Lightweight adaptive differential privacy (client-specific ε)
- Communication-efficient aggregation (gradient compression, selective updates)
- Enhanced CNN-LSTM hybrid model
- Adaptive aggregation weights based on client data quality

## Implementation Details

- **Framework:** PyTorch (custom FedAvg; no TFF required)
- **Dataset:** UNSW-NB15 — real training-partition download via `scripts/download_data.py --real`, or `--synthetic` fallback
- **Local Simulation:** Multi-process simulation of federated clients (no AWS required)
- **Privacy:** Opacus-compatible DP helpers in code paths
- **Deployment:** Local simulation only (no Docker/K8s/AWS executed)

## Experiments

1. **Pilot:** synthetic smoke (quarantined vs PoC)
2. **Centralised comparator:** `make centralised`
3. **Federated baseline + improved:** synthetic PoC
4. **Real UNSW sample:** `make unsw-real` (training-partition stratified sample)

## Dataset

**Primary:** UNSW-NB15 (Moustafa & Slay, 2015)  
**Download:** `python scripts/download_data.py --real` (public training-set mirror) or `--synthetic`  
Official project page: [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset)

## Results

### Synthetic PoC (`results/comparison/results.json`)

| Metric | Centralised | Baseline FL | Improved |
|--------|-------------|-------------|----------|
| Accuracy | 0.7975 | 0.793 | 0.800 |
| F1-Score | ≈0.015 | ≈0.019 | 0.0 |
| Avg Comm (MB/round) | 0.0 (N/A) | 1.83 | 3.12 |

### Real UNSW training-partition sample (`results/unsw_real/results.json`)

| Metric | Centralised | Baseline FL | Improved |
|--------|-------------|-------------|----------|
| Accuracy | 0.9452 | 0.8934 | 0.6800 |
| F1-Score | 0.9603 | 0.9262 | 0.8095 |
| Avg Comm (MB/round) | 0.0 (N/A) | 3.08 | 3.12 |

See `RESULTS_NOTE.md` / `STATUS.md`. Do not cite Saklani 91–94% as this artefact's result. Improved FL underperformance on the real sample is intentional honesty.

## Testing

```bash
make test
```

Tests include:
- Data loading and preprocessing
- Model creation
- Privacy helpers
- Centralised comparator smoke
- Privacy mechanism validation (gradient clipping, noise injection)
- Federated aggregation correctness
- Model training convergence
- End-to-end simulation

## Documentation

- `docs/CONFIGURATION_MANUAL.md`: Setup and configuration guide
- `docs/ARCHITECTURE.md`: System architecture and design
- `docs/EXPERIMENTS.md`: Experiment design and methodology

## Deployment Notes

- **Local Simulation (Default / only executed):** No cloud resources needed
- **Docker / Kubernetes / Helm:** Not present in this repo; do not claim container or K8s deployment
- **AWS:** Not deployed. Terraform scaffold at `terraform/` exists but has **not** been applied
- See `STATUS.md` and `RESULTS_NOTE.md` for honest PoC metrics (acc ~0.793/0.800, F1 near 0)

## Privacy Guarantees

- **Differential Privacy:** (ε, δ)-DP with ε ∈ [0.5, 2.0], δ = 1e-5
- **Secure Aggregation:** Model updates only, no raw data transmission
- **Client Isolation:** Each client trains on local data only

## Limitations and Future Work

- Current implementation: Honest-but-curious threat model (no Byzantine resilience)
- Local simulation only; Terraform at `terraform/` exists but is not applied; no Docker/K8s
- Binary/limited multi-class classification (could extend to zero-day detection)
- No concept drift handling (future: continuous learning mechanisms)

## Citation

If you use this work, please cite:

```bibtex
@mastersthesis{vikani2026secureflids,
  author = {Vikani, Nemi Ishwarlal},
  title = {SecureFL-IDS: A Privacy-Preserving Federated Intrusion Detection Framework for Cloud-Native Environments},
  school = {National College of Ireland},
  year = {2026},
  type = {MSc Research Project}
}
```

## License

This is academic research software. See `LICENSE` for details.

## Author

Nemi Ishwarlal Vikani  
Email: x24303046@student.ncirl.ie  
MSc Cloud Computing, National College of Ireland
