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
│   ├── __init__.py
│   ├── metadata/                     # S3 metadata collection
│   │   ├── __init__.py
│   │   └── collector.py             # Boto3-based object metadata extraction
│   ├── recommendation/               # Storage-class recommendation
│   │   ├── __init__.py
│   │   ├── baseline.py              # TierBase-inspired rule-based recommender
│   │   └── ml_recommender.py        # ML-enhanced recommender (XGBoost)
│   ├── forecasting/                  # Cost forecasting
│   │   ├── __init__.py
│   │   ├── naive_baseline.py        # Naive persistence baseline
│   │   └── time_series.py           # Prophet/ARIMA forecasting
│   ├── savings/                      # Savings estimation
│   │   ├── __init__.py
│   │   └── estimator.py             # Cost delta calculation
│   ├── pricing/                      # AWS pricing data
│   │   ├── __init__.py
│   │   └── s3_pricing.py            # S3 storage class pricing
│   ├── evaluation/                   # Evaluation harness
│   │   ├── __init__.py
│   │   └── metrics.py               # Accuracy, MAPE, RMSE, savings
│   ├── simulator/                    # Local simulator (dry-run mode)
│   │   ├── __init__.py
│   │   ├── s3_simulator.py          # Simulated S3 bucket
│   │   └── workload_generator.py    # Synthetic access pattern generator
│   └── runner/                       # Experiment orchestration
│       ├── __init__.py
│       └── experiment.py            # Main experiment runner
├── configs/
│   ├── pilot.yaml                   # Quick pilot run
│   ├── baseline.yaml                # Baseline experiment
│   ├── improved.yaml                # Improved framework experiment
│   └── pricing.json                 # AWS S3 pricing data (2026)
├── scripts/
│   ├── scaffold.sh                  # Setup script
│   ├── run_experiment.sh           # Run single experiment
│   └── run_all.sh                  # Run all experiments
├── tests/
│   ├── __init__.py
│   ├── test_metadata.py
│   ├── test_recommendation.py
│   ├── test_forecasting.py
│   ├── test_savings.py
│   └── test_integration.py
├── analysis/
│   ├── statistics.py                # Statistical tests (Wilcoxon, etc.)
│   └── plotting.py                  # Results visualization
├── docs/
│   ├── ARCHITECTURE.md              # System architecture
│   └── CONFIGURATION_MANUAL.md      # Configuration guide
└── results/                         # Committed results (not empty!)
    ├── data/                        # Raw experiment data (JSON/CSV)
    │   ├── pilot_results.json
    │   ├── baseline_results.json
    │   └── improved_results.json
    └── figures/                     # Generated figures (PNG)
        ├── cost_comparison.png
        ├── forecast_accuracy.png
        ├── allocation_accuracy.png
        └── savings_distribution.png
```

## Features

### 1. Metadata Collection
- Extracts object size, age, storage class, access frequency from S3
- Works with local simulator (DRY_RUN=1) or live AWS (DRY_RUN=0)
- Boto3-based implementation

### 2. Baseline Recommendation (TierBase-inspired)
- Rule-based storage-class selection based on:
  - Object age (days since last access)
  - Access frequency (moving average)
  - Object size
- Thresholds derived from TierBase methodology

### 3. Improved ML Recommendation
- XGBoost classifier trained on object features
- Predicts optimal storage class for each object
- Includes decision audit log

### 4. Cost Forecasting
- Time-series forecasting (Prophet/ARIMA)
- **Naive persistence baseline** (per Beck et al., 2025)
- MAPE and RMSE metrics vs baseline

### 5. Savings Estimation
- Calculates expected $ savings before applying recommendations
- Compares current vs. recommended storage class costs
- Uses AWS Pricing API data

### 6. Evaluation
- **Storage-class allocation accuracy**: % correctly allocated
- **Forecast error**: MAPE/RMSE vs naive baseline
- **Realized cost savings**: $ and % reduction
- **Statistical testing**: Wilcoxon signed-rank test (α=0.05)

## Experiment Modes

### Dry-Run Mode (Default)
No AWS account required. Uses synthetic access logs and simulated S3 bucket.

```bash
export DRY_RUN=1  # Default
make pilot
```

### Live AWS Mode (Optional)
Requires AWS credentials and active S3 bucket.

```bash
export DRY_RUN=0
export AWS_PROFILE=your-profile
export S3_BUCKET=your-test-bucket
make pilot
```

**Note:** Live AWS mode is documented but not required for this research. All committed results are from the local simulator with clearly-labeled synthetic data.

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
