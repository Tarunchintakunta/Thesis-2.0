# Project Status: Varun Gampa — S3 Cost Optimization

**Student:** Varun Gampa (23398639)  
**Programme:** MSc in Cloud Computing, National College of Ireland  
**Project:** Predictive Storage Cost Optimization Framework for Amazon S3  
**Last Updated:** 2026-09-20

## Overall status: NOT COMPLETE (CA2 alignment < 100%)

**Research alignment after claim hygiene:** ~70% — synthetic dry-run evidence locked to committed JSON; LaTeX/STATUS/README overclaims softened.  
**Not SUBMIT-READY.** Live S3 / Wilcoxon / Cost Explorer path and forecast `beats_naive` remain blockers.

Authoritative evidence: `s3-predictive-optimization/results/data/{pilot,baseline,improved}_results.json` (`mode: dry_run` only).

| Issue | Status |
|-------|--------|
| STATUS “100% complete” | **Demoted** — CA2 live-AWS RQ unmet |
| LaTeX filler / “successfully validated” | Softened to dry-run honesty |
| README phantom `src/metadata/`, `analysis/statistics.py` | Corrected to on-disk tree |
| `refs.bib` + `note={doi:…}` | Added under `latex_report/` |
| Live S3 / CE / CloudWatch / Wilcoxon | **Residual** — not run (do not deploy until gate) |
| Forecast beats naive | **Fails** on committed runs (`beats_naive: false`) |

---

## What is completed (local simulator)

1. Recommendation (TierBase-inspired rules + XGBoost), Prophet + naive forecast, savings estimator, local S3 simulator, experiment runner.
2. **20** pytest tests collected/passing locally.
3. Three committed dry-run experiments (pilot / baseline / improved) with figures.
4. Docs: README, ARCHITECTURE, CONFIGURATION_MANUAL; Terraform scaffold under `s3-predictive-optimization/terraform/` (**not applied**).

## Committed dry-run metrics (do not invent live AWS)

| Experiment | Allocation acc. | Forecast MAPE | Beats naive | Savings % (sim) |
|------------|----------------:|--------------:|:-----------:|----------------:|
| Pilot (100 obj, 30d) | 0.320 | 21.04 | **No** | 42.4 |
| Baseline rules (1000, 90d) | 0.504 | 21.73 | **No** | 21.0 |
| Improved ML (1000, 90d) | 0.178 | 21.73 | **No** | 57.4 |

Savings metadata may say “AWS Pricing API”; implementation uses local `configs/pricing.json`.

## What is NOT done

1. Live S3 Inventory / Boto3 metadata collector path (`src/metadata/` **absent**).
2. Live Cost Explorer / CloudWatch validation.
3. Wilcoxon multi-workload success protocol (no `analysis/statistics.py` on disk).
4. CA2 success bar: Prophet does **not** beat naive on committed runs.
5. Terraform apply / any AWS spend.

## Remaining blockers to 100%

1. Keep report/STATUS locked to dry-run JSON (no live overclaim).
2. Honest forecast narrative (`beats_naive: false`).
3. **AWS residual (yes):** live S3 FinOps evaluation once alignment-first gate allows.

```bash
cd Varun/s3-predictive-optimization
make test
# DRY_RUN=1 only until gate + budget approval
```
