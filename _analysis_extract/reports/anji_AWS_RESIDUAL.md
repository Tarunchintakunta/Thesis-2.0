# Anji alignment residual (AWS-goal)

**Updated:** 2026-09-20 (live lite key-cells measured; stack destroyed)  
**Alignment:** **~94/100** (was ~90% post packaging-dedup; was ~78% before)  
**Status:** **NOT COMPLETE**

## Compact
`RQ9 Obj12 Method13 Impl13 Exp11 Metrics10 Evidence11 Claims8 Rubric7` → **~94/100**

## Live AWS inventory (evidence-only)

Path: `anji-thesis/sqs-reliability-recovery/results/live/key_cells/`

| Artifact | Present |
|----------|---------|
| Manifests (4) | yes — `manifests/*.json`, `backend: live` |
| Raw events/produced/samples | yes — `raw/<run_id>/` |
| `run.log` | yes — 4/4 done in 772.3 s |
| `summary.json` / `summary.csv` / `live_key_cells_summary.json` | yes |
| Terraform after round | **destroyed** (state serial 43, 0 resources; no `sqs-rr*` Lambda/SQS) |

### Measured cells (n=1; order_count=200; region eu-west-1)

| Cell | loss | dup | DLQ | recovery_s | thr | usd |
|------|-----:|----:|----:|-----------:|----:|----:|
| consumer_kill VT30 MRC5 | 0.0 | 0.015 | 0.0 | 2.343 | 2.824/s | 0.000387 |
| consumer_kill VT90 MRC5 | 0.0 | 0.005 | 0.0 | 7.532 | 1.537/s | 0.000382 |
| unhandled_error VT30 MRC1 | 0.0 | 0.0 | **0.16** | censored | 7.122/s | 0.000311 |
| unhandled_error VT30 MRC5 | 0.0 | **0.05** | 0.0 | 28.506 | 2.920/s | 0.000362 |

**Lite round:** complete (4/4 planned in `configs/live_key_cells.yaml`).  
**Measured USD sum:** ≈ **$0.00144**.

Directional only (do not cite as confirmatory): longer VT → longer measured recovery under consumer_kill; MRC1 → DLQ 0.16 vs MRC5 → DLQ 0.0 with higher duplicates under unhandled_error; loss 0.0 on all four.

## Hygiene already done (localsim)
- 350 design vs 690 on-disk packaging twins reconciled
- H3_recovery fail-to-reject after Holm; twin-inflated rejects withdrawn
- DIVE / adaptive_vt not claimed

## Top blockers to 100%
1. **Confirmatory live** (repeats > 1) and/or **CA2-depth key cells** (`configs/key_cells.yaml` burst / VT 600 / MRC 10) — lite smoke ≠ full residual closure
2. Live↔sim fidelity writeup with explicit non-overclaim
3. Optional soft: adaptive_vt only if DIVE re-introduced

**Do not mark sole AWS residual closed:** lite 4-cell n=1 is necessary but not sufficient for 100% CA2 alignment.

```
GATE_READY=yes
LIVE_LITE_COMPLETE=yes
LIVE_CONFIRMATORY=no
AWS_CLASS=required
SOLE_AWS_RESIDUAL=partial
DESTROY_AFTER_ROUND=yes
```

Evidence: `STATUS.md`, `results/live/key_cells/summary.json`, `latex_report/text/evaluation.tex` (live section), `results/summary/stats_H1_H2_H3.json` (`runs: 350`).
