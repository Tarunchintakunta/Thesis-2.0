# Project Status: uday-thesis (iot-reliability)

**Last Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Research Alignment to CA2:** **~90%** (proxy via `../CA2_COMMITMENTS.md`; formal CA2 **NOT FOUND**)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMIT-READY)

## Summary

Local synthetic multi-site QoS campaign reproduces centralized RF (Et-Tousy et al. 2026) and evaluates federated ensemble + single-site lower bound. **No live AWS / OneM2M.** Absolute accuracies are high because labels are deterministic functions of features — relative ordering is the claim.

## Evidence-bound results (seeds 42–46)

Source: `results/results_summary.csv` (+ `results_per_seed.csv`).

| Model | Accuracy | Macro-F1 | Critical Recall (class 2) |
|--------|---------:|---------:|-------------------------:|
| Centralized RF (baseline) | 0.9995 ± 0.0005 | 0.9996 ± 0.0005 | 0.9994 ± 0.0013 |
| Federated Ensemble RF | 0.9959 ± 0.0024 | 0.9949 ± 0.0024 | 0.9997 ± 0.0007 |
| Single-Site Local Only | 0.9761 ± 0.0046 | 0.9737 ± 0.0051 | 0.9958 ± 0.0031 |

## What is done
- Simulator + RF arms; 5-seed driver; pytest; Makefile
- LaTeX report (TikZ figures may still be commented); bib `note={doi:…}`
- Root `uday-thesis/CA2_COMMITMENTS.md` + `baseline_papers/BASELINE_PAPER.md`

## Blockers to 100% (non-AWS)
1. Formal CA2 missing
2. Synthetic telemetry only (no Azure/OneM2M traces)
3. Prefer publisher JNSM PDF over Research Square preprint on disk
4. Soft: TikZ uncomment/debug; secure aggregation / weighted FL; Lambda never deployed (**do not deploy**)

## AWS
**Not on AWS deploy list.** Residual: `_analysis_extract/reports/uday_alignment.md`.
