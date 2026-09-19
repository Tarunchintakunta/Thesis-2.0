# SecureFL-IDS Configuration Manual

## Prerequisites

- Python 3.9+
- pip and virtualenv
- 4GB RAM minimum (8GB recommended for full experiments)
- 2GB disk space

## Installation

### Quick Setup

```bash
make install
```

This creates a virtual environment and installs all dependencies.

### Manual Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Dataset Configuration

### Synthetic Sample (Default)

For quick testing without external downloads:

```bash
python scripts/download_data.py --sample
```

Creates a synthetic 5K sample dataset at `data/UNSW_NB15_training-set.csv`.

### Full UNSW-NB15 Dataset

1. Download from: https://research.unsw.edu.au/projects/unsw-nb15-dataset
2. Place `UNSW_NB15_training-set.csv` in `data/` directory
3. Run without `--sample` flag:

```bash
python scripts/download_data.py
```

## Experiment Configuration

### Pilot Experiment (Quick)

```bash
make pilot
```

Configuration:
- 3 clients
- 10 rounds
- 3000 samples
- Runtime: ~1 minute

### Full Experiment

```bash
make experiment
```

Configuration:
- 5 clients
- 50 rounds
- 25000 samples
- Runtime: ~15 minutes

### Custom Configuration

Edit `configs/experiment_config.yaml` (or modify scripts directly):

```python
config = {
    'num_clients': 5,
    'num_rounds': 50,
    'local_epochs': 1,
    'learning_rate': 0.001,
    'epsilon': 1.0,
    'sample_size': 25000
}
```

## Privacy Parameters

### Baseline (Saklani et al. 2026)

```python
BaselineFLIDS(
    num_clients=5,
    epsilon=1.0,      # Privacy budget
    delta=1e-5,       # Privacy parameter
    clip_norm=1.0     # Gradient clipping threshold
)
```

### Improved (SecureFL-IDS)

```python
SecureFLIDS(
    num_clients=5,
    base_epsilon=1.0,              # Base privacy budget
    communication_efficient=True,   # Enable gradient compression
    compression_ratio=0.5          # Keep top 50% of gradients
)
```

## Communication Efficiency

### Standard FedAvg (Baseline)

All gradients transmitted without compression.

### Communication-Efficient (Improved)

Top-k gradient compression:
- `compression_ratio=0.5`: Keep 50% of gradients (recommended)
- `compression_ratio=0.3`: More aggressive compression
- `compression_ratio=1.0`: No compression

## Running Tests

```bash
make test
```

Or with pytest directly:

```bash
source .venv/bin/activate
pytest tests/ -v
```

## Generating Figures

After experiments complete:

```bash
make figures
```

Outputs to `figures/`:
- `convergence.png`: Accuracy/F1 convergence
- `communication_cost.png`: Communication overhead
- `comparison_bar.png`: Baseline vs improved comparison

## AWS Deployment (Optional)

**Note:** Current implementation focuses on local simulation. AWS deployment code is provided but not tested on live infrastructure.

### Prerequisites

- AWS account with appropriate credentials
- AWS CLI configured
- Docker installed

### Setup

1. Configure AWS credentials:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

2. Deploy (experimental):
```bash
# Build Docker images
docker-compose build

# Deploy to ECS (not yet implemented)
# aws ecs create-cluster --cluster-name securefl-ids
```

## Kubernetes Deployment (Experimental)

**Note:** K8s deployment is experimental and requires additional configuration.

### Prerequisites

- Kubernetes cluster (minikube/kind for local)
- kubectl configured
- Helm (optional)

### Deploy

```bash
# Create namespace
kubectl create namespace securefl-ids

# Deploy (Helm chart not yet provided)
# helm install securefl-ids ./helm/
```

## Troubleshooting

### Issue: Dataset not found

**Solution:** Run `python scripts/download_data.py --sample` first.

### Issue: Out of memory

**Solution:** Reduce `sample_size` in experiment config:
```python
sample_size=5000  # Instead of 25000
```

### Issue: Slow training

**Solution:** Use GPU if available:
```python
device = 'cuda' if torch.cuda.is_available() else 'cpu'
```

Or reduce model complexity by adjusting parameters in `src/common/models.py`.

### Issue: Import errors

**Solution:** Ensure virtual environment is activated:
```bash
source .venv/bin/activate
```

## Performance Tuning

### CPU Optimization

```python
import torch
torch.set_num_threads(4)  # Adjust based on CPU cores
```

### Batch Size Tuning

In `src/common/federated.py`, adjust:
```python
self.data_loader = DataLoader(dataset, batch_size=64, shuffle=True)
# Increase batch_size for faster training (if memory allows)
```

### Number of Local Epochs

More local epochs = less communication but slower convergence:
```python
local_epochs=1  # Fast, more communication
local_epochs=5  # Slower, less communication
```

## Contact

For issues or questions:
- Student: Nemi Ishwarlal Vikani
- Email: x24303046@student.ncirl.ie
- Institution: National College of Ireland
