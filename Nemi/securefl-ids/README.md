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

This command:
- Creates a virtual environment
- Installs dependencies
- Downloads and preprocesses a sample of the dataset
- Runs a pilot experiment (3 clients, 10 rounds)
- Displays results

## Full Usage

```bash
make test          # Run unit tests
make experiment    # Run full local experiment (baseline + improved)
make stats         # Generate statistical analysis
make figures       # Create evaluation figures
```

## Project Structure

```
securefl-ids/
├── src/
│   ├── baseline/         # Saklani et al. (2026) implementation
│   ├── improved/         # Enhanced SecureFL-IDS
│   ├── common/           # Shared utilities (data, metrics, FL orchestration)
│   └── data/             # Dataset download and preprocessing
├── tests/                # Unit and integration tests
├── configs/              # Experiment configurations (pilot, full, ablation)
├── scripts/              # Setup, data download, experiment runners
├── docs/                 # Configuration manual, architecture
├── results/              # Experiment outputs (metrics, logs)
└── figures/              # Evaluation plots
```

## Key Features

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
- Multi-class classification (normal + attack types)

## Implementation Details

- **Framework:** PyTorch (preferred over TensorFlow Federated for ease of installation)
- **Dataset:** UNSW-NB15 (subset included; full dataset download script provided)
- **Local Simulation:** Multi-process simulation of federated clients (no AWS required)
- **Privacy:** Opacus library for differential privacy
- **Deployment:** Local multi-process simulation only (no Docker/K8s/AWS executed)

## Experiments

All experiments run locally by default:

1. **Pilot:** 3 clients, 10 rounds, 1000 samples per client
2. **Baseline Replication:** Reproduce Saklani et al. results
3. **Improved Evaluation:** SecureFL-IDS vs baseline
4. **Ablation Studies:** 
   - Privacy budget impact (ε = 0.5, 1.0, 2.0)
   - Communication efficiency gains
   - Client heterogeneity scenarios

## Dataset

**Primary:** UNSW-NB15 (Moustafa & Slay, 2015)
- 9 attack types, 49 features
- 2.5M records (subset provided: 100K records)
- Non-IID distribution: clients have different attack type proportions

**Download:** Automated via `scripts/download_data.sh` or manual from [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset)

## Results

### Actual Results (Committed in `results/`)

**30-round experiment with synthetic data:**

| Metric | Baseline | Improved |
|--------|----------|----------|
| Accuracy | 79.3% | 80.0% |
| F1-Score | 1.9% | 0.0% |
| Avg Comm (MB/round) | 1.83 | 3.12 |

⚠️ **Note**: Low F1-scores due to synthetic dataset limitations. See `RESULTS_NOTE.md` for details.

### Baseline-paper reference only (NOT achieved by this PoC)

Saklani et al. (2026) report ~91–94% accuracy / ~90% F1 on full UNSW-NB15. **This repository has not run that campaign.** Do not cite those figures as SecureFL-IDS results. Committed PoC: accuracy 0.793/0.800, F1 near 0 (table above).

## Testing

```bash
make test
```

Tests include:
- Data loading and preprocessing
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
