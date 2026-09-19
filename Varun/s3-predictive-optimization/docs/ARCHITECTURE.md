# System Architecture

## Overview

The S3 Predictive Cost Optimization Framework is a modular system that combines storage-class recommendation, time-series cost forecasting, and savings estimation into a unified pipeline.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INPUT: S3 Bucket / Simulator                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      METADATA COLLECTION MODULE                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  • Object size, age, storage class                               │  │
│  │  • Access frequency, last access time                            │  │
│  │  • AWS SDK (Boto3) / Local Simulator                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐  ┌──────────────────────┐  ┌──────────────────┐
│   BASELINE      │  │   ML RECOMMENDER     │  │  COST HISTORY    │
│  RECOMMENDER    │  │                      │  │   GENERATOR      │
│                 │  │  • XGBoost           │  │                  │
│  • TierBase     │  │  • Feature           │  │  • Time-series   │
│    rules        │  │    engineering       │  │    data          │
│  • Age/access   │  │  • Training pipeline │  │                  │
│    thresholds   │  │                      │  │                  │
└────────┬────────┘  └──────────┬───────────┘  └────────┬─────────┘
         │                      │                        │
         └──────────────┬───────┴────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   RECOMMENDATION ENGINE OUTPUT                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  • Recommended storage class per object                          │  │
│  │  • Confidence scores (ML) / Reasoning (Baseline)                 │  │
│  │  • Decision audit log                                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
┌───────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   FORECASTING     │  │     SAVINGS      │  │   EVALUATION     │
│     MODULE        │  │   ESTIMATION     │  │     MODULE       │
│                   │  │                  │  │                  │
│  • Prophet        │  │  • Cost delta    │  │  • Allocation    │
│  • Naive baseline │  │  • AWS pricing   │  │    accuracy      │
│  • MAPE/RMSE      │  │  • vs Lifecycle  │  │  • Forecast      │
│                   │  │  • vs Intelligent│  │    MAPE/RMSE     │
│                   │  │    Tiering       │  │  • Cost savings  │
└─────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      RESULTS & REPORTING                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  • JSON experiment results                                       │  │
│  │  • Statistical tests (Wilcoxon)                                  │  │
│  │  • Visualization (PNG figures)                                   │  │
│  │  • Audit trail                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Metadata Collection Module
**Location:** `src/metadata/collector.py`  
**Purpose:** Extract S3 object attributes

**Inputs:**
- S3 bucket (live) or simulated bucket (dry-run)
- CloudWatch metrics (optional, live mode only)

**Outputs:**
- Object metadata: size, age, storage class, access frequency

**Technology:**
- AWS SDK (Boto3) for live mode
- Local simulator for dry-run mode

### 2. Recommendation Engine

#### 2a. Baseline Recommender (TierBase-inspired)
**Location:** `src/recommendation/baseline.py`  
**Reference:** Shen et al. (2025), TierBase, ICDE 2025

**Algorithm:**
```
IF size < 128 KB THEN
    STANDARD (avoid minimum size charges)
ELSE IF access_frequency > threshold THEN
    STANDARD (hot data)
ELSE IF age < 30 days AND age >= 30 THEN
    STANDARD_IA (warm data)
ELSE IF age >= 90 AND age < 180 THEN
    GLACIER_INSTANT (cold, occasional access)
ELSE IF age >= 180 THEN
    GLACIER_DEEP_ARCHIVE (long-term archive)
END
```

#### 2b. ML Recommender
**Location:** `src/recommendation/ml_recommender.py`  
**Reference:** Yang et al. (2025), MLSys 2025

**Features:**
- `object_size_mb`: Object size in megabytes
- `age_days`: Days since creation
- `access_frequency`: Accesses per month
- `access_recency`: Days since last access
- `days_since_creation`: Object age

**Model:** XGBoost multi-class classifier

**Training:**
- Ground truth labels generated via cost-optimal analysis
- 70/30 train/test split
- Cross-validation

### 3. Cost Forecasting Module

#### 3a. Naive Persistence Baseline
**Location:** `src/forecasting/naive_baseline.py`  
**Reference:** Beck, Dovern & Vogl (2025), Applied Intelligence

**Algorithm:** `forecast[t] = actual[t-1]` (all future = last observed)

**Purpose:** Prevent inflated accuracy claims

#### 3b. Time-Series Forecaster
**Location:** `src/forecasting/time_series.py`  
**Method:** Facebook Prophet

**Features:**
- Trend detection
- Seasonality (weekly)
- Confidence intervals (95%)
- Horizon: 30 days (configurable)

### 4. Savings Estimation
**Location:** `src/savings/estimator.py`

**Calculations:**
```
savings_usd = current_cost - recommended_cost
savings_pct = (savings_usd / current_cost) * 100

Comparison baselines:
- Current unoptimized configuration
- AWS Lifecycle Policies (age-based rules)
- AWS Intelligent-Tiering (simulated)
```

### 5. Evaluation Module
**Location:** `src/evaluation/metrics.py`

**Metrics:**
- **Allocation:** Accuracy, Precision, Recall, F1-Score
- **Forecasting:** MAPE, RMSE, MAE (vs naive baseline)
- **Cost:** Absolute and percentage savings
- **Statistical:** Wilcoxon signed-rank test (α=0.05)

## Data Flow

1. **Input:** S3 objects (live or simulated)
2. **Metadata:** Extract object characteristics
3. **Recommendation:** Apply baseline or ML method
4. **Forecasting:** Predict future costs
5. **Savings:** Estimate cost delta
6. **Evaluation:** Compare against baselines
7. **Output:** JSON results + PNG figures

## Execution Modes

### Dry-Run Mode (Default)
- `DRY_RUN=1`
- Uses local simulator
- Synthetic workload generation
- No AWS credentials required
- Free to run

### Live AWS Mode
- `DRY_RUN=0`
- Requires AWS credentials
- Real S3 bucket access
- Actual pricing data
- Incurs AWS charges

## Technology Stack

- **Language:** Python 3.11+
- **ML:** XGBoost, scikit-learn
- **Forecasting:** Prophet, statsmodels
- **Cloud:** Boto3 (AWS SDK)
- **Analysis:** pandas, numpy
- **Visualization:** matplotlib, seaborn
- **Testing:** pytest
- **Config:** YAML

## Key Design Decisions

1. **Modular Architecture:** Each component is independent and testable
2. **Dry-Run First:** Default to local simulator for reproducibility
3. **Naive Baseline Required:** Ensures honest forecast evaluation
4. **Audit Trail:** All recommendations include reasoning
5. **Statistical Rigor:** Wilcoxon test for significance
6. **Reproducible:** Fixed random seeds, versioned config

## Performance Characteristics

- **Pilot (100 objects):** ~2 seconds
- **Full (1000 objects):** ~5 seconds
- **Memory:** < 500 MB
- **Disk:** Results ~5 MB per experiment

## Future Extensions

1. Multi-cloud support (GCS, Azure Blob)
2. Real-time streaming updates
3. RL-based adaptive optimization
4. Integration with AWS Cost Explorer API
5. Automated CI/CD pipeline for recommendations
