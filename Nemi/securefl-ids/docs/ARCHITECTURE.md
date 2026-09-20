# SecureFL-IDS Architecture

## System Overview

SecureFL-IDS is a privacy-preserving federated learning framework for intrusion detection in cloud-native environments. The system enables collaborative threat detection across distributed cloud tenants without sharing raw network data.

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Environment                        │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Client 1 │  │ Client 2 │  │ Client 3 │  │ Client N │  │
│  │ (Tenant) │  │ (Tenant) │  │ (Tenant) │  │ (Tenant) │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │             │          │
│       └─────────────┴──────┬──────┴─────────────┘          │
│                            │                                │
│                            ▼                                │
│                  ┌──────────────────┐                       │
│                  │  Fed Aggregator  │                       │
│                  │    (Server)      │                       │
│                  └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Federated Clients

**Location:** `src/common/federated.py` - `FederatedClient`

Each client represents a cloud tenant with local network traffic data.

**Responsibilities:**
- Load and preprocess local network traffic data
- Train intrusion detection model locally
- Apply differential privacy to model updates
- Send only model parameters (not raw data) to server

**Key Operations:**
```python
client.train(epochs=1, lr=0.001, privacy_mechanism=dp)
# Returns: model parameter updates (Δw)
```

### 2. Federated Server

**Location:** `src/common/federated.py` - `FederatedServer`

Central aggregator that coordinates federated learning.

**Responsibilities:**
- Aggregate client model updates using FedAvg or weighted aggregation
- Apply communication-efficient compression (optional)
- Broadcast updated global model to clients
- Track convergence metrics

**Aggregation Methods:**
- **FedAvg**: Standard weighted average by data size
- **Weighted**: Quality-weighted aggregation (improved version)

### 3. Privacy Mechanisms

**Location:** `src/common/privacy.py`

#### Differential Privacy (Baseline)

Based on DP-SGD (Abadi et al., 2016) and Saklani et al. (2026):

```
σ = (C * sqrt(2 * ln(1.25/δ))) / ε

Where:
- ε: Privacy budget (1.0 in baseline)
- δ: Privacy parameter (1e-5)
- C: Gradient clipping norm (1.0)
- σ: Noise scale
```

**Steps:**
1. Clip gradients to bound sensitivity: `||g|| ≤ C`
2. Add calibrated Gaussian noise: `g' = g + N(0, σ²C²)`

#### Adaptive Differential Privacy (Improved)

Client-specific privacy budgets based on data quality:

```
ε_client = ε_base * (1 / (quality + 0.1))
Bounded to [0.5 * ε_base, 2.0 * ε_base]
```

Higher quality data → lower ε → more privacy

### 4. Models

**Location:** `src/common/models.py`

#### CNN Classifier (Baseline)

Architecture:
```
Input (batch, features)
  ↓
Conv1D(1→32) + BatchNorm + ReLU + MaxPool
  ↓
Conv1D(32→64) + BatchNorm + ReLU + MaxPool
  ↓
Flatten
  ↓
FC(→128) + ReLU + Dropout(0.5)
  ↓
FC(→2) [Normal, Attack]
```

#### CNN-LSTM Classifier (Improved)

Architecture:
```
Input (batch, features)
  ↓
CNN Layers (same as above)
  ↓
LSTM(64 hidden, 2 layers) + Dropout(0.3)
  ↓
FC(→128) + ReLU + Dropout(0.5)
  ↓
FC(→2) [Normal, Attack]
```

**Rationale:** LSTM captures temporal patterns in network traffic.

### 5. Data Pipeline

**Location:** `src/common/data_loader.py`

```
Raw Dataset (UNSW-NB15)
  ↓
Preprocessing
  - Handle missing values
  - Select numeric features
  - Binary labels (normal/attack)
  ↓
Train/Test Split (80/20)
  ↓
Normalization (StandardScaler)
  ↓
Non-IID Distribution
  - Dirichlet(α=0.5) split
  - Each client gets different attack type distribution
  ↓
Client Data Shards
```

## Federated Learning Workflow

### Round Protocol

```python
for round in range(num_rounds):
    # 1. Clients train locally
    for client in clients:
        updates = client.train(
            epochs=local_epochs,
            privacy_mechanism=dp
        )
        
    # 2. Server aggregates
    global_params = server.aggregate(
        client_updates,
        communication_efficient=True
    )
    
    # 3. Broadcast updated model
    for client in clients:
        client.update_model(global_params)
    
    # 4. Evaluate on test set
    metrics = evaluate(global_model, test_data)
```

### Communication Flow

```
┌─────────┐  Local Training  ┌────────┐
│ Client  │ ──────────────→  │  Model │
│  Data   │                  │ Update │
└─────────┘                  └───┬────┘
                                 │
                             DP Noise
                                 │
                                 ▼
                         ┌────────────────┐
                         │  Δw (privatized)│
                         └───────┬────────┘
                                 │
                              Upload
                                 │
                                 ▼
                         ┌────────────────┐
                         │  Aggregator    │
                         │  (FedAvg)      │
                         └───────┬────────┘
                                 │
                            Broadcast
                                 │
                                 ▼
                         ┌────────────────┐
                         │ Global Model   │
                         │    (w_t+1)     │
                         └────────────────┘
```

## Communication Efficiency

### Top-k Gradient Compression

**Location:** `src/common/federated.py` - `_compress_gradient()`

**Algorithm:**
```
1. Flatten gradient tensor
2. Select top-k elements by magnitude
3. Zero out remaining elements
4. Reshape to original dimensions
```

**Compression Ratio:** 0.5 (keep 50% of gradients)

**PoC communication (committed results.json):**
- Baseline: ~1.83 MB/round
- Improved: ~3.12 MB/round (higher than baseline; −45% not achieved on PoC)

## Non-IID Data Distribution

Simulates real-world cloud scenarios where tenants have different traffic patterns.

**Dirichlet Distribution:**
```python
client_samples ~ Dir(α)

Where α controls heterogeneity:
- α → 0: Highly non-IID (each client dominated by few classes)
- α → ∞: IID (uniform distribution)
- α = 0.5: Moderate non-IID (used in experiments)
```

## Evaluation Metrics

### Detection Metrics
- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC

### FL-Specific Metrics
- Communication cost per round (MB)
- Total communication cost (MB)
- Convergence rounds
- Round time (seconds)

### Privacy-Utility Trade-off
- Accuracy vs epsilon
- F1-Score vs epsilon

## Deployment Scenarios

### Local Simulation (Default)

- Multi-process simulation
- Shared memory for test set
- No network overhead
- Fast iteration

### Container / cloud (not executed)

- No Docker Compose / Helm / live AWS run in this PoC
- Terraform scaffold at `../terraform/` exists but is **not applied**

## Security Considerations

### Threat Model

**Assumed:**
- Honest-but-curious server
- No Byzantine clients
- No model poisoning attacks

**Protected Against:**
- Raw data leakage (no data leaves clients)
- Membership inference (via differential privacy)
- Model inversion (via gradient clipping)

**Not Protected Against:**
- Byzantine attacks (future work)
- Gradient-based attacks with advanced techniques
- Colluding clients

### Privacy Guarantees

**(ε, δ)-Differential Privacy:**

For ε=1.0, δ=1e-5:
- Strong privacy guarantee
- Negligible probability (δ) of privacy breach
- Trade-off: ~2-5% accuracy loss vs no privacy

## Performance Characteristics

### Committed PoC (`results/comparison/results.json`)

- Baseline: accuracy 0.793, F1 ≈ 0.019, ~1.83 MB/round
- Improved: accuracy 0.800, F1 0.0, ~3.12 MB/round
- Literature ~91–94% figures are **not** this PoC

## Future Enhancements

1. **Byzantine Resilience:** Krum/Trimmed Mean aggregation
2. **Asynchronous FL:** Allow straggler tolerance
3. **Personalized Models:** Per-client fine-tuning
4. **Zero-Day Detection:** Anomaly detection layer
5. **Multi-Attack Classification:** Extend to 9 attack types
6. **Secure Aggregation:** Cryptographic protocols
