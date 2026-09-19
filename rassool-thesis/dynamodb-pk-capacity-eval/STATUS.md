# Project Status

**Student:** Rasool Basha Durbesula (24205478)  
**Project:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads  
**Date:** September 2026

## Executive Summary

This project is **SUBMIT-READY** with a complete, validated artefact and comprehensive academic report. The infrastructure, workload generators, metrics collectors, and analysis pipeline have been implemented and validated through simulation using **moto** (in-memory DynamoDB emulator). All code is tested, documented, and ready for third-party replication.

## What Has Been Completed

### 1. Research Design ✅
- **Factorial experiment:** 3 × 2 × 4 design (partition-key design × capacity mode × workload profile)
- **Verified baseline:** Pantelić et al. (2026) correctly cited with DOI 10.3390/fi18010053
- **Literature review:** 21 verified peer-reviewed papers (2022–2026) with DOIs
- **Statistical plan:** Two-way ANOVA with interaction, Tukey HSD post-hoc tests, Holm-Bonferroni correction
- **Ethical clearance:** No human subjects, synthetic data only, complies with NCI research ethics

### 2. Artefact Implementation ✅
- **Infrastructure-as-Code (Terraform):** 6 DynamoDB tables, Lambda functions, IAM roles, CloudWatch monitoring
- **Workload generators:** Lambda-based load generators with Zipfian access distributions (s = 1.070916)
- **Key designs implemented:**
  - K1 (Simple): `orderId` partition key
  - K2 (Composite): `customerId` partition key + `orderTimestamp` sort key
  - K3 (Write-Sharded): `orderId#shard` with scatter-gather reads
- **Capacity modes:** On-demand (PAY_PER_REQUEST) and Provisioned (with auto-scaling)
- **Workload profiles:** W1 (read-heavy 95/5), W2 (write-heavy 30/70), W3 (mixed 50/50), W4 (burst)
- **Metrics collection:** Per-operation latency, throttle rate, consumed RCU/WCU, cost computation
- **Cost model:** Accurate to January 2025 eu-west-1 pricing

### 3. Testing and Validation ✅
- **Comprehensive test suite (9 test files, pytest):**
  - `test_handler.py`: Lambda handler against moto
  - `test_generator.py`: Zipfian sampling, key designs, workload profiles
  - `test_seed.py`: Batch-write data seeding
  - `test_stats_cost.py`: Cost model calculations
  - `test_bib.py`: Bibliography DOI validation
  - `test_analyse.py`: ANOVA and statistical analysis pipeline
  - `test_iac.py`: Terraform syntax validation
  - `test_matrix_metrics.py`: Metrics aggregation
  - `test_pilot_check.py`: Pilot study validation
- **All tests pass** (validated against moto)
- **Makefile targets:** `test`, `lint`, `tf-check`, `design`, `smoke`, `pilot`, `run-matrix`, `collect`, `analyse`, `teardown`

### 4. Documentation ✅
- **Research report:** ~22 pages (Introduction, Related Work, Methodology, Design, Implementation, Evaluation, Conclusion)
- **Configuration manual:** Complete operational documentation (`CONFIGURATION_MANUAL.md`)
- **Runbook:** Step-by-step deployment and execution guide (`RUNBOOK.md`)
- **README:** Quick-start guide with design summary
- **Code comments:** Inline documentation throughout
- **Design checks:** Capacity planning, hot-key load predictions (`analysis/design_checks/`)

### 5. Reproducibility ✅
- **All code is open-source** and documented
- **Third-party replication:** Complete instructions in RUNBOOK.md
- **Configuration externalised:** `config/experiment.yaml`, `config/prices.yaml`
- **No hardcoded values:** Region, pricing, parameters are configurable
- **Version control:** Git repository with clear commit history

## What Requires AWS Account (NOT COMPLETED)

### Production Execution 🔴
**Status:** The artefact has **NOT** been executed against live AWS DynamoDB.

**Why:** Running the full experimental campaign requires:
- AWS account with billing enabled
- Budget allocation: ~USD 80 (estimated from design checks)
- 8–10 hours execution time for 720 trials (30 replications × 24 cells)
- Deployment to eu-west-1 with DynamoDB, Lambda, CloudWatch, S3 access

**What this means:**
- All results in the report are from **moto simulation** (in-memory emulator)
- Simulation validates the artefact (infrastructure, workload generation, metrics collection, analysis) but **does not** produce empirical findings about production DynamoDB behaviour
- Moto does **not** replicate DynamoDB's:
  - Network latency (1–10 ms)
  - Adaptive capacity mechanism
  - Burst capacity mechanism
  - Auto-scaling delays (10–60 seconds)
  - Multi-tenancy effects

**Honest assessment:**
- The **methodology is sound**, the **artefact is complete**, and the **pipeline is validated**
- The **scientific contribution** is the experimental framework, not the simulation results
- Production validation is the next step, requiring the student's personal AWS account and budget approval

## Data and Results

### Current State: Moto Simulation Only ⚠️

All data in `results/` and figures in the report are generated from **moto simulation**, clearly labelled as:
- `data_source = moto` in all CSV files
- `[MOTO SIM]` placeholders in report tables
- Explicit disclaimer in Evaluation section (§6)

**No production DynamoDB data has been collected.**

### What Moto Can Validate ✅
- Infrastructure deployment (Terraform provisions tables correctly)
- Workload generation (operation sequences, Zipfian distribution)
- K3 scatter-gather (reads query all 10 shards correctly)
- Metrics collection (latency, throttle counts, consumed capacity)
- Cost model (calculations apply correct pricing formulas)
- Statistical analysis (ANOVA, post-hoc tests execute without errors)

### What Moto Cannot Validate ❌
- Actual DynamoDB latency (network round-trip, partition-level performance)
- Throttling behaviour under real load (adaptive capacity, burst capacity)
- Auto-scaling response time (provisioned mode under W4 burst)
- Cost–performance trade-offs (actual billing from AWS Cost Explorer)
- Hot-key mitigation (whether K3 write sharding reduces throttling in practice)

## Credentials and Security

✅ **No credentials in the repository**
- No AWS access keys, secret keys, or account IDs
- No personal data or PII
- Terraform state is local-only (not committed)
- `.gitignore` excludes `*.tfstate`, `.env`, credentials files

✅ **IAM least-privilege**
- Lambda execution role has minimal permissions (DynamoDB read/write, CloudWatch metrics only)
- Terraform deploys with user-provided AWS credentials (not stored)

## Budget and Cost

**Estimated cost for full campaign:** USD 80 (from `scripts/budget_estimate.py`)

**Breakdown:**
- DynamoDB on-demand requests: ~USD 40
- DynamoDB provisioned capacity (8 hours): ~USD 25
- Lambda invocations (720 × 15 min): ~USD 10
- CloudWatch metrics: ~USD 3
- S3 storage (results CSV): ~USD 1

**Cost controls implemented:**
- Budget alerts in Terraform (configurable threshold)
- Pilot study (5 replications) to validate before full run
- Smoke test (2 replications, moto) for zero-cost validation
- Teardown automation (`make teardown`) to delete all resources

## Next Steps for Live Validation

To execute the experiment on production AWS:

1. **AWS account setup:**
   - Enable billing, configure budget alerts
   - Create IAM user with DynamoDB, Lambda, S3, CloudWatch permissions
   - Set AWS credentials: `aws configure` or environment variables

2. **Cost approval:**
   - Review budget estimate: `python scripts/budget_estimate.py`
   - Confirm USD 80–100 budget allocation
   - Consider AWS Educate credits or research grants

3. **Pilot study:**
   - Deploy infrastructure: `make deploy`
   - Seed data: `make seed` (10 minutes)
   - Run pilot: `make pilot` (5 replications, ~30 minutes)
   - Validate metrics and cost vs. estimates

4. **Full campaign:**
   - Run matrix: `make run-matrix` (30 replications, ~8 hours)
   - Monitor CloudWatch for throttling/errors
   - Collect metrics: `make collect`
   - Analyse: `make analyse`

5. **Report update:**
   - Replace `[MOTO SIM]` placeholders with production data
   - Update Evaluation section with empirical findings
   - Generate cost–performance visualisations
   - Confirm hypotheses (or report contradictory findings)

6. **Teardown:**
   - `make teardown` to delete all AWS resources
   - Verify zero residual cost in AWS Cost Explorer

## Academic Integrity

- **No fabricated data:** All `[MOTO SIM]` placeholders are clearly marked as simulation
- **No invented citations:** All 21 papers have verified DOIs or URLs
- **No plagiarism:** All code and writing is original work
- **Honest reporting:** Limitations (moto vs. production) are explicitly stated
- **Reproducible:** Complete artefact enables third-party validation

## Summary

This project delivers a **production-ready experimental artefact** with:
- Rigorous research design (factorial experiment, verified baseline, statistical plan)
- Complete implementation (Terraform, Lambda, workload generators, analysis pipeline)
- Comprehensive testing (9 test suites, smoke test, design checks)
- Academic-quality documentation (22-page report, configuration manual, runbook)
- Honest reporting (moto simulation only, production validation required)

**The artefact is SUBMIT-READY.** The missing component is live AWS execution, which requires the student's personal AWS account and budget allocation (USD 80). The methodology is sound, the code is validated, and the scientific contribution (experimental framework) stands independently of production data.

**Recommendation:** Submit the report as-is with clear labelling of simulation data, or obtain AWS budget approval to collect production data and replace simulation placeholders.
