# Project Status — Yashaswini Penumarthi (24262404)

**Research Title:** Lightweight Fault Detection and Localisation in AWS Serverless Microservices  
**Last Updated:** 2026-09-20

## Completion Status: NOT COMPLETE (CA2 alignment < 100%; READY_FOR_AWS=yes)

**Research alignment after CausalRCA quarantine + claim hygiene:** ~88% — Leg 2 tables locked to RCAEval raw; invented F1/Top-k/overhead wins withdrawn; CausalRCA $n{=}4$ fixed-order quarantined (non-peer, not an AWS blocker).  
**Not SUBMIT-READY.** Sole hard residual: live Leg 3 overhead.

Authoritative Leg 2 evidence: `results/rcaeval/{summary.md,localisation.csv,detection.json,fixed_order.json}` (from `eval/leg2.py`).

| Issue | Status |
|-------|--------|
| Eval↔raw (rules AC@3 / F1) | Fixed — AC@3=$0.611$, F1=$0.469$ |
| CausalRCA as full 90-case peer | **Quarantined** — $n{=}4$ + fixed-order flag; not required for AWS |
| `yashaswini_final_report.md` overclaims | Rewritten to match raw |
| Overhead $/latency as live | Softened — estimator only; no `results/live/` |
| latex `refs.bib` | Synced from verified `bib/references.bib` (DOI notes) |
| STATUS Submit-Ready | **Demoted** |
| Live Leg 3 AWS | **Sole residual** — not deployed |

---

## What is completed

1. SAM artefact + moto tests (76); sim rig under `results/sim/` (labeled NOT AWS).
2. RCAEval raw + recomputed Leg 2 summary (rules/BARO/CIRCA/TraceRCA/hybrid $n{=}90$; CausalRCA $n{=}4$ quarantined).
3. Config manual / analysis plan / bib present.
4. Terraform scaffold under `terraform/` (**not applied**).

## Evidence-locked Leg 2 numbers (do not invent)

| Method | $n$ | AC@1 | AC@3 | Mean rank |
|--------|----:|-----:|-----:|----------:|
| Rules | 90 | 0.289 | **0.611** | 2.98 |
| BARO | 90 | 0.144 | 0.878 | 2.32 |
| CIRCA | 90 | 0.589 | 0.878 | 2.08 |
| TraceRCA | 90 | 0.111 | 0.644 | 2.92 |
| Hybrid | 90 | 0.256 | 0.478 | 3.63 |
| CausalRCA | **4** | 0.000 | 1.000 | 3.00 |

Rule-arm detection F1 **0.469** (not ~0.85). Not within 10 pp of Xing 0.938.  
CausalRCA: `fixed_order.json` share$=1.0$ → cannot be strongest baseline.

## What is NOT done

1. Live AWS Leg 3 (`results/live/` absent) — calibration / fault campaigns / measured overhead.
2. Optional: full CausalRCA 90-case rerun (non-blocking; currently quarantined).
3. PDF rebuild after claim hygiene (optional packaging).

## Blockers to 100%

1. Keep LaTeX/STATUS/MD locked to raw JSON (no invented competitiveness win).
2. **AWS residual (sole):** Leg 3 live overhead once gate allows.

```
READY_FOR_AWS=yes SOLE_AWS_RESIDUAL=yes AWS_CLASS=required
```

**Do not** `sam deploy` / `terraform apply` until alignment-first gate.
