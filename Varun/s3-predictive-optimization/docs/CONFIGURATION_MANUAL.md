# Configuration Manual

## Overview

This manual describes all configuration options for the S3 Predictive Cost Optimization Framework.

## Configuration Files

All configuration files are located in `configs/`:

- `pilot.yaml` - Quick pilot run (100 objects, 30 days)
- `baseline.yaml` - TierBase baseline experiment (1000 objects, 90 days)
- `improved.yaml` - ML + forecasting experiment (1000 objects, 90 days)
- `pricing.json` - AWS S3 pricing data (2026 prices, us-east-1)

## YAML Configuration Structure

### Experiment Section

```yaml
experiment:
  name: "experiment_name"              # Human-readable name
  description: "Brief description"     # What this experiment does
  mode: "dry_run"                      # dry_run or live_aws
```

### Workload Section

Defines the synthetic workload characteristics.

```yaml
workload:
  num_objects: 1000                    # Number of S3 objects to simulate
  duration_days: 90                    # Simulation period in days
  access_patterns:                     # Distribution of access patterns
    - hot: 0.15                        # 15% frequently accessed
    - warm: 0.35                       # 35% occasionally accessed
    - cold: 0.50                       # 50% rarely accessed
  size_distribution:                   # Object size distribution
    mean_mb: 25                        # Mean size in MB
    std_mb: 15                         # Standard deviation
    min_mb: 0.1                        # Minimum size
    max_mb: 500                        # Maximum size
```

**Access Pattern Definitions:**
- **Hot:** 50-200 accesses/month, age 1-30 days
- **Warm:** 5-50 accesses/month, age 30-180 days
- **Cold:** 0-5 accesses/month, age 180-720 days

### Recommendation Section

Configure the recommendation engine.

```yaml
recommendation:
  method: "ml"                         # baseline, ml, or both
  
  baseline:                            # TierBase-inspired thresholds
    age_threshold_ia: 30               # Days before → STANDARD_IA
    age_threshold_glacier_instant: 90  # Days before → GLACIER_INSTANT
    age_threshold_glacier_deep: 180    # Days before → GLACIER_DEEP
    access_threshold_ia: 5             # Max accesses/month for IA
    access_threshold_glacier: 1        # Max accesses/month for Glacier
    size_threshold_kb: 128             # Minimum size for tiering
  
  ml:                                  # ML recommender config
    model: "xgboost"                   # XGBoost classifier
    train_fraction: 0.7                # 70% training, 30% test
    features:                          # Feature list
      - object_size_mb
      - age_days
      - access_frequency
      - access_recency
      - days_since_creation
    hyperparameters:
      max_depth: 6
      learning_rate: 0.1
      n_estimators: 100
```

**Recommendation Methods:**
- `baseline`: Rule-based TierBase algorithm only
- `ml`: XGBoost ML classifier only
- `both`: Run both methods, use ML for final recommendation

### Forecasting Section

Configure cost forecasting.

```yaml
forecasting:
  enabled: true                        # Enable/disable forecasting
  method: "prophet"                    # prophet or arima
  horizon_days: 30                     # Forecast horizon
  naive_baseline: true                 # Always compare vs naive
  confidence_interval: 0.95            # 95% confidence intervals
```

**Forecasting Methods:**
- `prophet`: Facebook Prophet (recommended)
- `arima`: ARIMA time-series model

**Important:** `naive_baseline` should always be `true` to ensure honest evaluation per Beck et al. (2025).

### Savings Section

Configure savings estimation.

```yaml
savings:
  enabled: true                        # Enable savings estimation
  estimation_method: "delta_pricing"   # Cost delta calculation
  compare_against:                     # Baseline comparisons
    - current_unoptimized
    - aws_lifecycle
    - aws_intelligent_tiering
```

### Evaluation Section

Configure evaluation metrics and statistical tests.

```yaml
evaluation:
  metrics:                             # Metrics to calculate
    - allocation_accuracy              # % correctly allocated
    - precision                        # Classification precision
    - recall                           # Classification recall
    - f1_score                         # F1-score
    - forecast_mape                    # Mean Absolute % Error
    - forecast_rmse                    # Root Mean Squared Error
    - cost_savings_usd                 # Absolute savings
    - cost_savings_percent             # Percentage savings
  statistical_test: "wilcoxon"         # Statistical test
  alpha: 0.05                          # Significance level
  compare_baseline: true               # Compare vs baseline
```

**Statistical Tests:**
- `wilcoxon`: Wilcoxon signed-rank test (paired, non-parametric)
- `ttest`: Paired t-test (parametric, assumes normality)

### Output Section

```yaml
output:
  results_dir: "results/data"          # JSON results directory
  figures_dir: "results/figures"       # PNG figures directory
  save_raw: true                       # Save raw experiment data
  save_audit_log: true                 # Save decision audit log
  save_model: true                     # Save trained ML model
```

## Environment Variables

Set via `.env` file or shell export:

```bash
DRY_RUN=1                    # 1=simulator, 0=live AWS (default: 1)
AWS_PROFILE=default          # AWS profile (live mode only)
AWS_REGION=us-east-1         # AWS region (live mode only)
S3_BUCKET=test-bucket        # Target S3 bucket (live mode only)
S3_PREFIX=test-data/         # Object prefix filter (live mode only)
RANDOM_SEED=42               # Random seed for reproducibility
```

## Pricing Configuration

File: `configs/pricing.json`

```json
{
  "storage_classes": {
    "STANDARD": {
      "storage_gb_month": 0.023,       # $/GB/month
      "retrieval_per_1000": 0.0004,    # $/1000 requests
      "min_storage_days": 0            # No minimum
    },
    "STANDARD_IA": {
      "storage_gb_month": 0.0125,
      "retrieval_per_1000": 0.001,
      "min_storage_days": 30,          # 30-day minimum
      "min_object_size_kb": 128        # 128 KB minimum
    },
    ...
  }
}
```

**Prices:** Based on AWS us-east-1 pricing as of 2026. Update periodically from [AWS Pricing](https://aws.amazon.com/s3/pricing/).

## Running Experiments

### Quick Start (Dry-Run)

```bash
# Setup
make setup

# Run pilot
make pilot

# Run all experiments
make experiments

# Generate figures
make figures
```

### Custom Configuration

```bash
# Create custom config
cp configs/pilot.yaml configs/my_experiment.yaml

# Edit configuration
vim configs/my_experiment.yaml

# Run
python3 src/runner/experiment.py \
    --config configs/my_experiment.yaml \
    --output results/data/my_experiment_results.json
```

### Live AWS Mode

**Prerequisites:**
- AWS account with S3 access
- Configured AWS credentials (`aws configure`)
- Test S3 bucket

```bash
# Set environment
export DRY_RUN=0
export AWS_PROFILE=your-profile
export S3_BUCKET=your-test-bucket

# Run experiment
make pilot
```

**⚠️ Warning:** Live mode incurs AWS charges. Estimate costs first:
```bash
python3 scripts/estimate_cost.py --config configs/pilot.yaml
```

## Troubleshooting

### Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/s3-predictive-optimization
```

### Prophet Installation Fails

Prophet requires a C++ compiler. On Ubuntu:
```bash
sudo apt-get install python3-dev build-essential
pip3 install prophet
```

### AWS Credentials Not Found

```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=yyy
```

### Results Not Saved

Check write permissions on `results/` directory:
```bash
chmod -R u+w results/
```

## Best Practices

1. **Always start with dry-run mode** to validate configuration
2. **Use version control** for custom configs
3. **Document custom experiments** in config `description` field
4. **Save results** with descriptive names
5. **Compare against naive baseline** for forecasting
6. **Run statistical tests** for significance claims
7. **Update pricing data** periodically
8. **Test on small workloads** before scaling up

## Configuration Examples

### Minimal Pilot (Fast)

```yaml
experiment:
  name: "quick-test"
workload:
  num_objects: 50
  duration_days: 14
recommendation:
  method: "baseline"
forecasting:
  enabled: false
```

### Full Research Run (Comprehensive)

```yaml
experiment:
  name: "research-full"
workload:
  num_objects: 5000
  duration_days: 180
recommendation:
  method: "both"
forecasting:
  enabled: true
  method: "prophet"
  horizon_days: 60
evaluation:
  metrics: [all]
  statistical_test: "wilcoxon"
  compare_baseline: true
```

### Live AWS Production Test

```yaml
experiment:
  name: "production-test"
  mode: "live_aws"
workload:
  # Not used in live mode
recommendation:
  method: "ml"
savings:
  enabled: true
  compare_against:
    - current_unoptimized
    - aws_lifecycle
    - aws_intelligent_tiering
```

## Support

For questions or issues:
1. Check this manual
2. Review `README.md`
3. Check `docs/ARCHITECTURE.md`
4. Contact: X23398639@student.ncirl.ie
