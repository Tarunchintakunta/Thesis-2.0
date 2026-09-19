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

**Baseline Results:** 91.8% accuracy, F1-score >90% on UNSW-NB15 dataset with non-IID tenant distribution.

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
- **Deployment:** Docker-ready (docker-compose for multi-client simulation)

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

## Results (Local Simulation)

| Metric | Baseline | Improved | Δ |
|--------|----------|----------|---|
| Accuracy | 91.2% | 93.7% | +2.5% |
| F1-Score | 90.8% | 93.1% | +2.3% |
| Communication (MB/round) | 12.4 | 6.8 | -45.2% |
| Convergence (rounds) | 50 | 35 | -30% |

*Results from local experiments with 5 clients, 50 rounds, ε=1.0*

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

- **Local Simulation (Default):** No cloud resources needed
- **Docker:** `docker-compose up` for containerized clients
- **AWS (Optional):** See `docs/CONFIGURATION_MANUAL.md` for ECS deployment
- **Kubernetes:** Helm chart provided for K8s deployment (experimental)

## Privacy Guarantees

- **Differential Privacy:** (ε, δ)-DP with ε ∈ [0.5, 2.0], δ = 1e-5
- **Secure Aggregation:** Model updates only, no raw data transmission
- **Client Isolation:** Each client trains on local data only

## Limitations and Future Work

- Current implementation: Honest-but-curious threat model (no Byzantine resilience)
- Local simulation only (AWS deployment code provided but not tested on live infrastructure)
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
