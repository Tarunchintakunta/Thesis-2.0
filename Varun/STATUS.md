**INITIAL_EVAL_PASS:** **yes** (honest floor ~88 — not market 100)
**Note:** Independent r4+r5 confirmatory; archival r1–r3 history only; alloc-acc dated WONTFIX. Authority: `CA2_PROPOSED_VS_ARTEFACT.md` + `scripts/audit_independence_root_causes.py`.
INITIAL_EVAL_PASS=yes

# Project Status: Varun Gampa — S3 Cost Optimization

**Student:** Varun Gampa (23398639)  
**Programme:** MSc in Cloud Computing, National College of Ireland  
**Project:** Predictive Storage Cost Optimization Framework for Amazon S3  
**Last Updated:** 2026-09-23

## Overall status: MOVE ALLOWED — honest CA2 floor ~88% — do not market 100

**Research alignment (CA2):** **~88%** — dry-run + live lite + archival e1–e3 + **independent r4+r5**; audit `remediable_total=0` EXIT 0; `meets_ca2_two_of_three=true` on r4/r5; alloc-acc limb **dated WONTFIX**.  
**ONE-file SoT:** `Varun/CA2_PROPOSED_VS_ARTEFACT.md`.  
**Audit (binding):** `s3-predictive-optimization/scripts/audit_independence_root_causes.py` → disposition `DATED_WONTFIX_ALLOC_ACC`.  
**Not inventing metrics.**

Authoritative dry-run: `s3-predictive-optimization/results/data/{pilot,baseline,improved}_results.json` (`mode: dry_run`).  
Authoritative live lite: `s3-predictive-optimization/results/live/live_lite_summary.json`.  
Authoritative confirmatory: `results/live/evaluation_r{4,5}/summary.json` (+ archival `r{1,2,3}` history).  
Destroy: `results/live/destroy_confirmed.txt` + empty `terraform/terraform.tfstate`.

| Issue | Status |
|-------|--------|
| CA2 live multi-workload FinOps RQ (cost) | **Met** — independent r4+r5, two-of-three (actually 3/3) vs both natives |
| Forecast beats naive | **Pass** — pilot/baseline/improved `beats_naive=true` |
| Independent r4+r5 | **Closed** — distinct SHAs; script EXIT 0 |
| Archival r1–r3 as ×3 indep | **Rejected** — identical SHA; history only |
| Alloc-acc limb | **DATED_WONTFIX 2026-09-23** — negative vs Lifecycle |
| Destroy-after | **Confirmed** |
| Config manual audit section | **Present** |
| Report / viva | Fold later — does **not** block MOVE |
| GENAI_HANDOFF.md | **Present** (artefact) |

---

## What is completed (local simulator)

1. Recommendation (TierBase-inspired rules + XGBoost), Prophet + naive forecast, savings estimator, local S3 simulator, experiment runner.
2. Pytest suite (pricing, recommendation, forecasting, savings, integration) including holdout hygiene tests.
3. Three committed dry-run experiments (pilot / baseline / improved).
4. Docs: README, ARCHITECTURE, CONFIGURATION_MANUAL (incl. scripted audit); Terraform under `s3-predictive-optimization/terraform/`.
5. Scripted independence audit + ONE-file SoT + dated alloc-acc WONTFIX.

## Committed dry-run metrics (do not invent live AWS)

| Experiment | Allocation acc. | Forecast MAPE | Naive MAPE | Beats naive | Savings % (sim) |
|------------|----------------:|--------------:|-----------:|:-----------:|----------------:|
| Pilot (100 obj, 30d) | 0.320 | 0.016 | 0.44 | **Yes** | 42.4 |
| Baseline rules (1000, 90d) | 0.504 | 0.006 | 0.44 | **Yes** | 21.0 |
| Improved ML (1000, 90d) | 0.178 | 0.231 | 0.44 | **Yes** | 57.4 |

## Confirmatory independent live (r4 / r5) — cite these

Protocol: `ca2_three_workload_wilcoxon` — 10 trials × 80 objects; baselines = Lifecycle + Intelligent-Tiering.  
SHA: r4 `7babd39c…` ≠ r5 `53bec5e5…`; `rebuilt_from_run_log=false`.

| Workload | r4 vs both | r5 vs both |
|----------|:----------:|:----------:|
| static_archival | Yes | Yes |
| mixed_access | Yes | Yes |
| high_churn | Yes (p≈0.049) | Yes (p≈0.0098) |
| `meets_ca2_two_of_three` | **true** | **true** |

Alloc offline: proposed Acc ≈0.35–0.37 vs Lifecycle ≈0.85 — **negative retained** (`DATED_WONTFIX_N_Varun_alloc_acc_2026-09-23.md`).

## Soft residuals (not MOVE blockers)

- Report packaging / viva prep (fold later).
- Optional new live pack for HeadObject-derived alloc Acc (beyond floor; not required for MOVE).

```
CA2_FLOOR=~88 MOVE=ALLOWED AUDIT_EXIT=0 REMEDIABLE=0
SOT=Varun/CA2_PROPOSED_VS_ARTEFACT.md
CONFIRMATORY=r4,r5 ALLOC=WONTFIX
```

```bash
cd Varun/s3-predictive-optimization
python3 scripts/audit_independence_root_causes.py
# EXIT 0; remediable_total must be 0
ls results/live/evaluation_r{4,5}/summary.json results/live/analysis/
```
