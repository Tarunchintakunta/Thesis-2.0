# Live AWS Campaign Runbook

**Project:** lambda-idempotency-eval  
**Author:** Vikas Reddy Amanagantti (X25178849)  
**Status:** Ready for live deployment  
**Estimated cost:** ~USD 0.17 (see `make budget`)

---

## Prerequisites

### 1. AWS Credentials

Set AWS credentials via **one** of these methods:

```bash
# Option A: AWS Profile (recommended)
export AWS_PROFILE=your-profile-name

# Option B: Direct credentials
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=eu-west-1
```

**Verification:**
```bash
aws sts get-caller-identity
```

### 2. Required Permissions

Your IAM user/role needs:
- DynamoDB: CreateTable, UpdateTable, DeleteTable, PutItem, GetItem, DescribeTable
- Lambda: CreateFunction, UpdateFunctionCode, InvokeFunction, DeleteFunction
- IAM: CreateRole, AttachRolePolicy, DeleteRole
- CloudWatch: PutMetricAlarm, GetMetricStatistics
- Budgets: CreateBudget

See `docs/CONFIGURATION_MANUAL.md` for detailed permission requirements.

### 3. Python Environment

```bash
make setup  # Creates .venv and installs dependencies
```

### 4. Pre-flight Checks

```bash
make test       # All 63 tests must pass
make tf-check   # Terraform validation
make budget     # Review estimated spend
```

---

## Live Campaign: One-Command Path

### Quick Start (Complete Campaign)

```bash
# 1. Deploy infrastructure (creates DynamoDB table + Lambda function)
make deploy

# 2. Run pilot (150 requests → determines required sample size N)
make pilot && make pilot-size

# 3. Run full campaign (uses N from pilot, ~9000 requests at N=1000)
make campaign WORKERS=16

# 4. Run sensitivity test (P3 crash-between-writes case)
make sensitivity WORKERS=16

# 5. Collect CloudWatch metrics (wait ~10 minutes after campaign)
make cloudwatch

# 6. Analyse results and generate figures
make analyse

# 7. Tear down infrastructure
make destroy
```

**Total time:** ~30 minutes (mostly waiting for CloudWatch metric aggregation)

---

## Step-by-Step Walkthrough

### Step 1: Deploy Infrastructure

```bash
make deploy
```

**What it does:**
- Builds Lambda deployment package (`build/lambda.zip`)
- Runs `terraform apply` in `infra/`
- Creates:
  - DynamoDB table (`lambda-idempotency-eval-table-vikas`)
  - Lambda function (`lambda-idempotency-eval-vikas`, 256MB, 2s timeout, arm64)
  - IAM role with DynamoDB permissions
  - CloudWatch log group
  - Budget alarm (USD 1.00 threshold)
  - CloudWatch alarms for errors and throttles

**Expected output:**
```
Apply complete! Resources: 8 added, 0 changed, 0 destroyed.

Outputs:

function_arn = "arn:aws:lambda:eu-west-1:ACCOUNT:function:lambda-idempotency-eval-vikas"
table_name = "lambda-idempotency-eval-table-vikas"
```

**Credentials check:** Will fail with clear error message if AWS credentials not set.

---

### Step 2: Run Pilot

```bash
make pilot
```

**What it does:**
- Runs 150 requests (50 per path × 3 paths) at multiplicity 2 and 5
- Invokes Lambda 300 times (150 with injected timeout)
- Writes results to `data/runs/live/pilot/`
- Processes DynamoDB Streams to detect duplicate mutations

**Duration:** ~2-3 minutes

**Output files:**
- `data/runs/live/pilot/schedule.csv`
- `data/runs/live/pilot/deliveries.jsonl`
- `data/runs/live/pilot/stream.jsonl`
- `data/runs/live/pilot/run_info.json`

**Then determine required sample size:**

```bash
make pilot-size
```

**What it does:**
- Applies Wen et al. (2025) pilot-sizing rule
- Calculates required N for 95% CI width ≤ 0.10
- Writes decision to `results/live/pilot_choice.json`

**Expected output:**
```
Pilot sizing complete. Required N = 1000 per cell.
See results/live/pilot_report.md for details.
```

---

### Step 3: Run Full Campaign

```bash
make campaign WORKERS=16
```

**What it does:**
- Runs 9000 requests (1000 per path × 3 paths × 3 multiplicities)
- Invokes Lambda ~24,000 times (15,000 with injected timeout)
- Uses 16 parallel workers for faster execution
- Writes results to `data/runs/live/campaign/`

**Duration:** ~10-15 minutes with 16 workers

**Safety guards:**
- Hard limit: 60,000 invocations (driver refuses to exceed)
- Budget alarm: USD 1.00 (CloudWatch alert)
- Seed guard: deterministic `request_id` ensures exact replication

**Output files:**
- `data/runs/live/campaign/schedule.csv` (9000 rows)
- `data/runs/live/campaign/deliveries.jsonl` (~24,000 lines)
- `data/runs/live/campaign/stream.jsonl` (duplicate mutation records)
- `data/runs/live/campaign/run_info.json`

---

### Step 4: Run Sensitivity Test

```bash
make sensitivity WORKERS=16
```

**What it does:**
- Tests P3 (idempotency key) crash-between-writes scenario
- Timeout occurs BETWEEN checking the key and writing the business item
- 400 requests across multiplicities

**Duration:** ~2-3 minutes

**Output files:**
- `data/runs/live/sensitivity/deliveries.jsonl`
- `data/runs/live/sensitivity/stream.jsonl`

---

### Step 5: Collect CloudWatch Metrics

**IMPORTANT:** Wait ~10 minutes after campaign completes before running this step.  
CloudWatch metrics are not immediately available.

```bash
make cloudwatch
```

**What it does:**
- Queries CloudWatch Logs Insights for Lambda invocations, errors, timeouts
- Cross-checks with driver ground truth
- Writes comparison to `data/runs/live/campaign/cloudwatch.json`

**Duration:** ~30 seconds

---

### Step 6: Analyse Results

```bash
make analyse
```

**What it does:**
- Computes per-request and per-cell metrics
- Runs statistical tests (z-tests, chi-square, Mann-Whitney U, Welch t-test)
- Applies Holm–Bonferroni correction
- Evaluates pre-registered expectations E1-E3
- Generates tables and figures

**Output files (results/live/):**
- `summary.md` — Complete results report
- `cells.csv` — Per-cell duplicate rate, capacity, latency with CIs
- `dup_tests.csv`, `chi2.csv` — Family D tests
- `capacity_tests.csv`, `latency_tests.csv` — Family C and L tests
- `expectations.csv` — E1-E3 decisions
- `checks.csv` — Data quality checks
- `sensitivity_cells.csv`, `sensitivity_outcomes.csv` — Sensitivity results

**Output figures (figures/live/):**
- `dup_rate.png` — Duplicate mutation rate by path and multiplicity
- `latency.png` — End-to-end latency distributions
- `capacity.png` — Consumed write capacity units
- `surface.png` — Correctness-cost trade-off surface

**Duration:** ~10 seconds

---

### Step 7: Tear Down Infrastructure

```bash
make destroy
```

**What it does:**
- Runs `terraform destroy` in `infra/`
- Deletes DynamoDB table (data is not recoverable)
- Deletes Lambda function
- Deletes IAM role
- Deletes CloudWatch log group and alarms

**IMPORTANT:** Results in `data/runs/live/`, `results/live/`, and `figures/live/` are preserved locally. Back them up before destroying.

---

## Credential Check Behavior

All live AWS targets (`deploy`, `pilot`, `campaign`, `sensitivity`, `cloudwatch`, `destroy`) require AWS credentials.

**Without credentials:**
```bash
$ make deploy
ERROR: AWS credentials not found.
Set AWS_PROFILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY before running live targets.
See docs/CONFIGURATION_MANUAL.md for setup instructions.
make: *** [check-aws-creds] Error 1
```

**With credentials:**
```bash
$ make deploy
✓ AWS credentials detected
PY=.venv/bin/python scripts/build_lambda.sh
Building Lambda deployment package...
[... terraform output ...]
```

**Fail-closed design:** No live target will proceed without valid AWS credentials.

---

## Results Path Separation: Moto vs Live

| Path | Purpose | AWS Data? |
|------|---------|-----------|
| `results/moto/` | Functional validation (local mock) | ❌ NO |
| `results/live/` | **Real AWS measurements** | ✅ YES |
| `figures/moto/` | Figures from moto (validation only) | ❌ NO |
| `figures/live/` | **Figures from live AWS** | ✅ YES |

**Never conflate moto and live results.**

- Moto results prove the implementation works but do NOT answer the research question.
- Moto has no latency model (reports ~1 ms) and incorrect capacity units (always 0.5).
- Only `results/live/` contains AWS measurements suitable for the evaluation.

All output files carry a source label in their first line or metadata:
- Moto: `"source": "moto"` or "Source: moto functional check"
- Live: `"source": "live"` or "Source: AWS Lambda eu-west-1"

---

## Troubleshooting

### Credential errors
```
ERROR: AWS credentials not found.
```
→ Set `AWS_PROFILE` or `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`

### Terraform state conflicts
```
Error acquiring the state lock
```
→ Wait for any running `terraform apply` to complete, or manually remove `.terraform.tfstate.lock.info`

### "run make pilot-size first"
```
ERROR: run make pilot-size first (or pass N=...)
```
→ You must run `make pilot && make pilot-size` before `make campaign`  
→ Or override: `make campaign N=1000`

### Budget alarm triggered
→ Check AWS Budgets console  
→ Review `make budget` estimate vs actual spend  
→ Driver has hard limit at 60,000 invocations

### CloudWatch metrics not available
```
No data points found
```
→ Wait 10-15 minutes after campaign completes  
→ CloudWatch metric aggregation is not immediate

---

## Cost Estimate

See `make budget` for detailed breakdown. Provisional N=1000:

| Phase | Invocations | Estimated Cost (USD) |
|-------|-------------|---------------------|
| Pilot | 300 | 0.002 |
| Campaign | 24,000 | 0.157 |
| Sensitivity | 1,400 | 0.011 |
| **Total** | **25,700** | **~0.17** |

Based on eu-west-1 list prices as of 2026-09-11:
- Lambda: USD 0.0000000017 per ms + USD 0.20 per 1M requests (arm64)
- DynamoDB: USD 1.4269 per million write units (on-demand)
- Free tier NOT included in estimate

---

## Safety and Research Integrity

1. **No secrets in repository:** AWS credentials must be provided at runtime (environment variables)
2. **Bounded spend:** Hard limit at 60,000 invocations + USD 1.00 budget alarm
3. **Synthetic data only:** No human participants, no personal data
4. **Own account:** Researcher accepts cost responsibility
5. **Seed guard:** Deterministic `request_id` generation allows exact replication
6. **Moto validation first:** Always run `make functional` before deploying to AWS

---

## Quick Reference

```bash
# Full campaign (one-liner after credentials are set)
make deploy && make pilot && make pilot-size && make campaign WORKERS=16 && \
  make sensitivity WORKERS=16 && sleep 600 && make cloudwatch && make analyse

# Review results
cat results/live/summary.md
open figures/live/dup_rate.png

# Tear down
make destroy
```

---

**For detailed configuration, see:** `docs/CONFIGURATION_MANUAL.md`  
**For analysis methods, see:** `docs/ANALYSIS_PLAN.md`  
**For current status, see:** `STATUS.md`

Vikas Reddy Amanagantti  
Last updated: 2026-09-19
