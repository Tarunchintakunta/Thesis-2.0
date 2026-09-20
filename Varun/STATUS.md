# Project Status: Varun Gampa — S3 Cost Optimization

**Student:** Varun Gampa (23398639)  
**Programme:** MSc in Cloud Computing, National College of Ireland  
**Project:** Predictive Storage Cost Optimization Framework for Amazon S3  
**Last Updated:** 2026-09-20

## Overall status: NOT COMPLETE (CA2 alignment ~96%; READY_FOR_AWS=yes)

**Research alignment:** **~96%** — dry-run locked; live lite S3/CE/CW/Wilcoxon measured+destroyed; `src/metadata/` (lite JSON + Inventory CSV + Boto3 listing, moto-tested); local **3-workload Wilcoxon** protocol executed (`meets_ca2_two_of_three=true`; high-churn vs Lifecycle **not** significant).  
**Not SUBMIT-READY.** Residual: live Inventory *job* + CE-settled multi-workload campaign (Free Tier OK; **concurrency blocked** — Vikas r5 RUNNING). See `DESIGN_RATIONALE_BEYOND_CA2.md`.

Authoritative dry-run: `s3-predictive-optimization/results/data/{pilot,baseline,improved}_results.json` (`mode: dry_run`).  
Authoritative live lite: `s3-predictive-optimization/results/live/live_lite_summary.json`.  
Authoritative local 3-workload: `s3-predictive-optimization/results/data/multi_workload_wilcoxon.json`.

| Issue | Status |
|-------|--------|
| STATUS “100% complete” | **Demoted** — live Inventory/CE-settled campaign unmet |
| Forecast eval bug (flat round + synthetic actual) | **Fixed** — holdout + full float precision |
| `beats_naive` on pilot / baseline / improved | **Pass** (`true`) on all three |
| `src/metadata/` + Inventory CSV + Boto3 listing | **Present** (not a live Inventory job) |
| `analysis/statistics.py` 3-workload Wilcoxon | **Executed locally** n=10 |
| Live S3 / CE / CloudWatch / Wilcoxon | **Lite round DONE** (destroyed); full campaign residual remains |

---

## What is completed (local simulator)

1. Recommendation (TierBase-inspired rules + XGBoost), Prophet + naive forecast, savings estimator, local S3 simulator, experiment runner.
2. Pytest suite including holdout hygiene, Inventory CSV, moto Boto3 listing, 3-workload stats (27 tests).
3. Three committed dry-run experiments (pilot / baseline / improved).
4. Docs: README, ARCHITECTURE, CONFIGURATION_MANUAL, DESIGN_RATIONALE_BEYOND_CA2; Terraform under `s3-predictive-optimization/terraform/`.

## Committed dry-run metrics (do not invent live AWS)

| Experiment | Allocation acc. | Forecast MAPE | Naive MAPE | Beats naive | Savings % (sim) |
|------------|----------------:|--------------:|-----------:|:-----------:|----------------:|
| Pilot (100 obj, 30d) | 0.320 | 0.016 | 0.44 | **Yes** | 42.4 |
| Baseline rules (1000, 90d) | 0.504 | 0.006 | 0.44 | **Yes** | 21.0 |
| Improved ML (1000, 90d) | 0.178 | 0.231 | 0.44 | **Yes** | 57.4 |

Savings metadata may say “AWS Pricing API”; implementation uses local `configs/pricing.json`.

## Live lite round (2026-09-20, measured only)

Unchanged: 24× STANDARD + 24× STANDARD_IA; Wilcoxon cost p=9.63e-07; GET/PUT p=1.19e-07; CE sum $3.6e-09; destroy complete.

## Local 3-workload Wilcoxon (2026-09-20, simulator)

| Workload | vs Lifecycle | vs Intelligent-Tiering | vs both natives |
|----------|:------------:|:----------------------:|:---------------:|
| static_archival | p=0.00195 sig | p=0.00195 sig | **yes** |
| mixed_access | p=0.00195 sig | p=0.00195 sig | **yes** |
| high_churn | p=0.557 **n.s.** | p=0.00195 sig | no |

`meets_ca2_two_of_three=true`. High-churn vs Lifecycle mean Δ ≈ $6.5×10^{-5}$ — reported honestly. **Not** live buckets.

## What is NOT done

1. Live S3 Inventory *job* (parser exists; no Inventory configuration was applied).
2. Settled Cost Explorer validation of campaign savings (CE lag; lite ≠ savings trial).
3. Live multi-workload Wilcoxon on real trial buckets (local protocol ≠ live).

## Remaining blockers to 100%

1. Keep report/STATUS locked to committed JSON (dry-run + live lite + local Wilcoxon); no overclaim.
2. **AWS residual:** live Inventory job + CE-settled multi-workload campaign when concurrency is free.

```
READY_FOR_AWS=yes SOLE_AWS_RESIDUAL=yes AWS_CLASS=required
LIVE_LITE=done DESTROYED=yes LOCAL_3WORKLOAD=done
ALIGNMENT=~96
```

```bash
cd Varun/s3-predictive-optimization
make test
python analysis/statistics.py --n-trials 10 --objects-per-trial 80
# Live lite: python scripts/live_lite_round.py (after terraform apply) — do not apply while concurrency hot
```
