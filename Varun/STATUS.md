# Project Status: Varun Gampa — S3 Cost Optimization

**Student:** Varun Gampa (23398639)  
**Programme:** MSc in Cloud Computing, National College of Ireland  
**Project:** Predictive Storage Cost Optimization Framework for Amazon S3  
**Last Updated:** 2026-09-20

## Overall status: NOT COMPLETE (CA2 alignment < 100%; READY_FOR_AWS=yes)

**Research alignment:** ~90% — dry-run evidence locked; live lite S3/CE/CW/Wilcoxon probe executed and destroyed.  
**Not SUBMIT-READY.** Residual: full multi-workload live FinOps campaign (Inventory/metadata collector, settled CE savings, multi-workload Wilcoxon protocol).

Authoritative dry-run: `s3-predictive-optimization/results/data/{pilot,baseline,improved}_results.json` (`mode: dry_run`).  
Authoritative live lite: `s3-predictive-optimization/results/live/live_lite_summary.json`.

| Issue | Status |
|-------|--------|
| STATUS “100% complete” | **Demoted** — CA2 live-AWS RQ unmet |
| Forecast eval bug (flat round + synthetic actual) | **Fixed** — holdout + full float precision |
| `beats_naive` on pilot / baseline / improved | **Pass** (`true`) on all three |
| LaTeX filler / report depth | Softened — eval/design/impl evidence-locked |
| `refs.bib` + `note={doi:…}` | Present under `latex_report/` |
| Live S3 / CE / CloudWatch / Wilcoxon | **Lite round DONE** (destroyed); full campaign residual remains |

---

## What is completed (local simulator)

1. Recommendation (TierBase-inspired rules + XGBoost), Prophet + naive forecast, savings estimator, local S3 simulator, experiment runner.
2. Pytest suite (pricing, recommendation, forecasting, savings, integration) including holdout hygiene tests.
3. Three committed dry-run experiments (pilot / baseline / improved).
4. Docs: README, ARCHITECTURE, CONFIGURATION_MANUAL; Terraform under `s3-predictive-optimization/terraform/`.

## Committed dry-run metrics (do not invent live AWS)

| Experiment | Allocation acc. | Forecast MAPE | Naive MAPE | Beats naive | Savings % (sim) |
|------------|----------------:|--------------:|-----------:|:-----------:|----------------:|
| Pilot (100 obj, 30d) | 0.320 | 0.016 | 0.44 | **Yes** | 42.4 |
| Baseline rules (1000, 90d) | 0.504 | 0.006 | 0.44 | **Yes** | 21.0 |
| Improved ML (1000, 90d) | 0.178 | 0.231 | 0.44 | **Yes** | 57.4 |

Savings metadata may say “AWS Pricing API”; implementation uses local `configs/pricing.json`.

## Live lite round (2026-09-20, measured only)

| Surface | Measured |
|---------|----------|
| Region / bucket | `eu-west-1` / `s3-pred-opt-60d216643d19b67c00e7ffc8d0` |
| S3 objects | 24× STANDARD + 24× STANDARD_IA (160 KiB each); listed `KeyCount=48` |
| PUT mean ms | STANDARD **1008.3**; STANDARD_IA **681.6** |
| GET mean ms | STANDARD **187.2**; STANDARD_IA **524.2** |
| CE S3 Unblended (2026-09-13→20) | **sum $3.6e-09** (account window; not round savings) |
| CW metrics | API ok; `BucketSizeBytes` datapoints **[]** (new-bucket lag) |
| CW Logs | PutLogEvents ok → `/research/s3-pred-opt` stream `lite-20260920T120351Z` |
| Wilcoxon cost (n=24) | W=0, p=**9.63e-07**, significant (probe-scoped; not multi-workload) |
| Wilcoxon GET latency (n=24) | W=0, p=**1.19e-07**, significant |
| Wilcoxon PUT latency (n=24) | W=0, p=**1.19e-07**, significant |
| Modeled Δ storage $/mo (std−IA) | **3.845e-05** (list-rate model; not CE bill) |
| Destroy | **complete** (8 resources); empty terraform state; bucket absent |

Artefacts: `results/live/live_lite_summary.json`, `results/live/live_lite_raw.json`.

## What is NOT done

1. Live S3 Inventory / Boto3 metadata collector module (`src/metadata/` **absent**).
2. Settled Cost Explorer validation of campaign savings (CE lag; lite ≠ savings trial).
3. Multi-workload Wilcoxon success protocol (no `analysis/statistics.py`; lite is single-bucket probe).
4. Long-lived Terraform apply (destroyed after lite).

## Remaining blockers to 100%

1. Keep report/STATUS locked to committed JSON (dry-run + live lite); no overclaim.
2. **AWS residual:** full live S3 FinOps evaluation (Inventory + multi-workload Wilcoxon + CE-settled costs).

```
READY_FOR_AWS=yes SOLE_AWS_RESIDUAL=yes AWS_CLASS=required
LIVE_LITE=done DESTROYED=yes
```

```bash
cd Varun/s3-predictive-optimization
make test
# Live lite: python scripts/live_lite_round.py (after terraform apply)
```
