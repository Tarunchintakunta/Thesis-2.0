# Project Status: Varun Gampa — S3 Cost Optimization

**Student:** Varun Gampa (23398639)  
**Programme:** MSc in Cloud Computing, National College of Ireland  
**Project:** Predictive Storage Cost Optimization Framework for Amazon S3  
**Last Updated:** 2026-09-20

## Overall status: NOT COMPLETE (CA2 alignment < 100%; READY_FOR_AWS=yes)

**Research alignment after forecast-holdout fix + claim hygiene:** ~88% — dry-run evidence locked; Prophet beats naive on pilot/improved under temporal holdout; LaTeX filler demoted.  
**Not SUBMIT-READY.** Sole hard residual: live S3 / CE / CloudWatch / Wilcoxon campaign.

Authoritative evidence: `s3-predictive-optimization/results/data/{pilot,baseline,improved}_results.json` (`mode: dry_run`; `eval_protocol: temporal_holdout`).

| Issue | Status |
|-------|--------|
| STATUS “100% complete” | **Demoted** — CA2 live-AWS RQ unmet |
| Forecast eval bug (flat round + synthetic actual) | **Fixed** — holdout + full float precision |
| `beats_naive` on pilot / baseline / improved | **Pass** (`true`) on all three |
| LaTeX filler / report depth | Softened — eval/design/impl evidence-locked |
| `refs.bib` + `note={doi:…}` | Present under `latex_report/` |
| Live S3 / CE / CloudWatch / Wilcoxon | **Sole residual** — not run (do not deploy until gate) |

---

## What is completed (local simulator)

1. Recommendation (TierBase-inspired rules + XGBoost), Prophet + naive forecast, savings estimator, local S3 simulator, experiment runner.
2. Pytest suite (pricing, recommendation, forecasting, savings, integration) including holdout hygiene tests.
3. Three committed dry-run experiments (pilot / baseline / improved).
4. Docs: README, ARCHITECTURE, CONFIGURATION_MANUAL; Terraform scaffold under `s3-predictive-optimization/terraform/` (**not applied**).

## Committed dry-run metrics (do not invent live AWS)

| Experiment | Allocation acc. | Forecast MAPE | Naive MAPE | Beats naive | Savings % (sim) |
|------------|----------------:|--------------:|-----------:|:-----------:|----------------:|
| Pilot (100 obj, 30d) | 0.320 | 0.016 | 0.44 | **Yes** | 42.4 |
| Baseline rules (1000, 90d) | 0.504 | 0.006 | 0.44 | **Yes** | 21.0 |
| Improved ML (1000, 90d) | 0.178 | 0.231 | 0.44 | **Yes** | 57.4 |

Savings metadata may say “AWS Pricing API”; implementation uses local `configs/pricing.json`.

## What is NOT done

1. Live S3 Inventory / Boto3 metadata collector path (`src/metadata/` **absent**).
2. Live Cost Explorer / CloudWatch validation.
3. Wilcoxon multi-workload success protocol (no `analysis/statistics.py` on disk).
4. Terraform apply / any AWS spend.

## Remaining blockers to 100%

1. Keep report/STATUS locked to dry-run JSON (no live overclaim).
2. **AWS residual (sole):** live S3 FinOps evaluation once alignment-first gate allows.

```
READY_FOR_AWS=yes SOLE_AWS_RESIDUAL=yes AWS_CLASS=required
```

```bash
cd Varun/s3-predictive-optimization
make test
# DRY_RUN=1 only until gate + budget approval
```
