# Predictive Storage Cost Optimization Framework for Amazon S3

**Student:** Varun Gampa (23398639)  
**Programme:** MSc in Cloud Computing, National College of Ireland  
**Thesis Title:** Predictive Storage Cost Optimization Framework for Amazon S3: Intelligent Storage-Class Recommendation, Forecasting and Savings Estimation

## Overview

This project implements an integrated framework that combines:
1. **Storage-class recommendation** (baseline + ML-enhanced)
2. **Time-series cost forecasting** (with naive baseline comparison)
3. **Savings estimation** (before applying recommendations)

The framework addresses the limitations of AWS-native reactive tools (Lifecycle Policies and Intelligent-Tiering) by providing proactive, predictive cost management.

## Research Question

*To what extent does an integrated predictive storage-class optimisation framework – combining machine-learning-based storage-class recommendation, time-series-based cost forecasting, and savings estimation – reduce Amazon S3 storage cost and improve storage-class allocation accuracy, relative to AWS-native Lifecycle Policies and Intelligent-Tiering?*

## Quick Start (Local Simulator - No AWS Required)

```bash
# Setup environment
make setup

# Run tests
make test

# Run pilot experiment (synthetic data, dry-run mode)
make pilot

# Run full experiments
make experiments

# Generate statistics and figures
make stats figures

# Check all quality gates
make gates
```

## Project Structure

```
s3-predictive-optimization/
├── Makefile                          # Build and experiment targets
├── README.md                         # This file
├── requirements.txt                  # Python dependencies
├── requirements-dev.txt              # Development dependencies
├── pyproject.toml                    # Project metadata
├── .env.example                      # Example environment variables
├── src/
│   ├── recommendation/               # TierBase rules + XGBoost recommender
│   ├── forecasting/                  # Prophet + naive persistence baseline
│   ├── savings/                      # Delta-pricing savings estimator
│   ├── pricing/                      # Local list-price loader (`pricing.json`)
│   ├── evaluation/                   # Allocation / MAPE metrics
│   ├── simulator/                    # Synthetic S3 + workload generator
│   ├── runner/                       # Experiment orchestration
│   └── s3_storage_optimizer.py
├── configs/                          # pilot / baseline / improved YAML + pricing.json
├── tests/                            # 20 pytest tests (pricing, rec, forecast, savings, integration)
├── analysis/
│   └── plotting.py                   # Figures only (no Wilcoxon module on disk)
├── terraform/                        # Scaffold — **not applied**
├── docs/
│   ├── ARCHITECTURE.md
│   └── CONFIGURATION_MANUAL.md
└── results/
    ├── data/{pilot,baseline,improved}_results.json
    └── figures/*.png
```

**Not present (do not claim):** `src/metadata/collector.py`, `analysis/statistics.py`, live Boto3 Inventory path.

## Features (dry-run evidenced)

### 1. Local metadata / workload path
- Synthetic object features from `simulator/` (`DRY_RUN=1` only in committed runs)
- Live Boto3 metadata collector **not implemented** on disk

### 2. Baseline Recommendation (TierBase-inspired)
- Rule-based storage-class selection (age, access frequency, size)

### 3. Improved ML Recommendation
- XGBoost classifier; committed improved allocation accuracy **0.178**

### 4. Cost Forecasting
- Prophet vs **naive persistence** (Beck et al., 2025)
- Committed runs: **`beats_naive=false`** (MAPE ≈ 21%)

### 5. Savings Estimation
- Delta pricing from local `configs/pricing.json` (not a live Pricing API / Cost Explorer call)

### 6. Evaluation
- Allocation accuracy, MAPE/RMSE, simulated $ savings
- Wilcoxon multi-workload campaign **not executed** (no stats module committed)

## Experiment Modes

### Dry-Run Mode (Default)
No AWS account required. Uses synthetic access logs and simulated S3 bucket.

```bash
export DRY_RUN=1  # Default
make pilot
```

### Live AWS Mode (future / gated)
Documented as a residual under the alignment-first gate. **Do not run** until Research Alignment hits 100% or sole residual is live CA2 AWS. No live results are committed.

## Baseline Papers

This research builds upon and compares against:

1. **Shen et al. (2025)** - *TierBase: A Workload-Driven Cost-Optimized Key-Value Store*, ICDE 2025  
   DOI: [10.1109/ICDE65448.2025.00049](https://doi.org/10.1109/ICDE65448.2025.00049)

2. **Yang et al. (2025)** - *A Bring-Your-Own-Model Approach for ML-Driven Storage Placement in Warehouse-Scale Computers*, MLSys 2025  
   arXiv: [2501.05651](https://arxiv.org/abs/2501.05651)

3. **Liu et al. (2025)** - *SkyStore: Cost-Optimized Object Storage Across Regions and Clouds*, VLDB 2025  
   DOI: [10.14778/3734839.3734846](https://doi.org/10.14778/3734839.3734846)

## Dependencies

- Python 3.11+
- boto3 (AWS SDK)
- pandas, numpy
- scikit-learn, xgboost
- prophet (time-series forecasting)
- statsmodels (ARIMA)
- pytest (testing)
- matplotlib, seaborn (visualization)
- pyyaml (configuration)

## Results

All experiment results are **committed to this repository** in `results/`:
- Raw data (JSON/CSV) in `results/data/`
- Figures (PNG) in `results/figures/`

Results are generated from the **local simulator with synthetic S3 access logs** (clearly labeled as such in the data files and paper).

## Status

See [STATUS.md](../../STATUS.md) for honest % completion and details on what is simulated vs. live AWS.

## Citation

```bibtex
@mastersthesis{gampa2027s3optimization,
  author = {Gampa, Varun},
  title = {Predictive Storage Cost Optimization Framework for Amazon S3: 
           Intelligent Storage-Class Recommendation, Forecasting and Savings Estimation},
  school = {National College of Ireland},
  year = {2027},
  type = {MSc Thesis},
  address = {Dublin, Ireland}
}
```

## License

Academic use only. National College of Ireland, 2027.
