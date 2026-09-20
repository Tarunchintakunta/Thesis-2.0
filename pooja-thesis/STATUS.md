# Project Status: pooja-thesis

**Last Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Research Alignment to CA2:** **~85%** (proxy via `CA2_COMMITMENTS.md`; formal CA2 **NOT FOUND**)  
**Status:** **NOT COMPLETE** — **&lt;100%** (do **not** treat as SUBMISSION-READY / 100%)

## Summary

Local synthetic workload simulator reproduces NimbusGuard’s agility–instability **trade-off** with Aggressive PAKS vs Reactive HPA, then evaluates Stability-Aware PAKS (EMA + hysteresis/cooldown). **Not** a DQN+LSTM live K8s replication. **No live AWS.**

## Evidence-bound results (seeds 42–46)

Source: `paks-framework/results/results_summary.csv` (+ `results_per_seed.csv`).

| Model | SLA Violations | Over-prov. % | Scaling Events | Pod Volatility |
|--------|---------------:|-------------:|---------------:|---------------:|
| Reactive HPA | 20.0 ± 2.7 | 40.92 ± 0.19 | 407.4 ± 4.9 | 3.32 ± 0.25 |
| Aggressive PAKS | 11.0 ± 2.2 | 45.80 ± 2.23 | 384.4 ± 9.1 | 2.86 ± 0.36 |
| Stability-Aware PAKS | 18.0 ± 2.7 | 46.52 ± 2.16 | 165.8 ± 5.3 | 1.95 ± 0.17 |

Stability-Aware cuts scaling events ≈57% and volatility ≈32% vs Aggressive, at +7 SLA violations (still ≤ HPA).

## What is done
- Three policies + 5-seed driver; pytest suite; Makefile
- LaTeX report; bib `note={doi:…}` where DOI known
- `CA2_COMMITMENTS.md` + expanded `baseline_papers/BASELINE_PAPER.md`

## Blockers to 100% (non-AWS)
1. Formal CA2 missing (proxy commitments)
2. Method gap vs NimbusGuard (MLP simulator ≠ DQN+LSTM testbed)
3. Synthetic cyclical workloads only
4. Soft: live K8s validation; Lambda/SAM never applied (**do not deploy**)

## AWS
**Not on AWS deploy list.** Residual: `_analysis_extract/reports/pooja_alignment.md`.
