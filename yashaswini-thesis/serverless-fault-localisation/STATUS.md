# Project Status — Yashaswini Penumarthi (24262404)

**Research Title:** Lightweight Fault Detection and Localisation in AWS Serverless Microservices  
**Last Updated:** 2026-09-23  
**Honest CA2 floor:** **~72** — Leg2 locked; Leg3 lite measured; ≥0.50 **fails**; ≥0.35 amended; F1 gap + CausalRCA quarantine retained. Do **not** market 100.  
**SoT:** `../CA2_PROPOSED_VS_ARTEFACT.md` · **N-Yash WONTFIX:** `../DATED_WONTFIX_N_Yash_2026-09-23.md`  
**MOVE ALLOWED:** **yes** — `scripts/audit_leg3_reduction_root_causes.py` EXIT 0; remediable_total=0 (2026-09-23).

## Completion Status: **COMPLETE (honest ~72)** — beyond-CA2 optional

**Research alignment:** **~72** research-scope floor — Leg 2 tables locked to RCAEval raw; CausalRCA $n{=}4$ fixed-order quarantined (non-peer); **live Leg 3 overhead measured** under `results/live/final_{1,2,3}/overhead.json` (lite protocol); original reduction ≥0.50 **fails** on finals (0.383/0.422/0.472); amended ≥0.35 dated 2026-09-22. Soft: CausalRCA 90 / PDF rebuild — **beyond-CA2** (`DESIGN_RATIONALE_BEYOND_CA2.md`). **AWS residual: closed.**

**INITIAL_EVAL_PASS:** **yes** (lite Leg 3 + finals).  
**Final-3 progress:** `results/live/final_1|2|3/` **DONE** — baseline `FINAL3_BASELINE.md`.  
**Audit:** `results/live/analysis/leg3_reduction_audit_report.*`.

Authoritative Leg 2 evidence: `results/rcaeval/{summary.md,localisation.csv,detection.json,fixed_order.json}` (from `eval/leg2.py`).  
Authoritative Leg 3 evidence: `results/live/final_{1,2,3}/overhead.json` + `FINAL3_BASELINE.md`.  
Initial-eval gate: `results/live/initial_eval_1/`.

| Issue | Status |
|-------|--------|
| Eval↔raw (rules AC@3 / F1) | Fixed — AC@3=$0.611$, F1=$0.469$ |
| CausalRCA as full 90-case peer | **Quarantined** — $n{=}4$ + fixed-order flag; not required for AWS |
| `yashaswini_final_report.md` overclaims | Rewritten to match raw |
| Overhead $/latency as live | **Measured (lite finals)** — reduction fails 0.50; amended ≥0.35 |
| latex `refs.bib` | Synced from verified `bib/references.bib` (DOI notes) |
| Live Leg 3 AWS | **Done (lite)** — destroyed after rounds |
| Soft residuals | Optional CausalRCA 90; PDF rebuild; learned-LB **filled** ($n{=}8$ subset) |
| Scripted audit | EXIT 0 — disposition `DATED_WONTFIX_REDUCTION_050_FAIL_AMENDED_035` |

---

## What is completed

1. SAM artefact + moto tests (76); sim rig under `results/sim/` (labeled NOT AWS).
2. RCAEval raw + recomputed Leg 2 summary (rules/BARO/CIRCA/TraceRCA/hybrid $n{=}90$; CausalRCA $n{=}4$ quarantined).
3. Config manual / analysis plan / bib present.
4. Terraform `faultlab` stack applied for lite Leg 3, measured, **destroyed** (2026-09-20).
5. Lite Leg 3 overhead: 5 min × 3 conditions @ 1 rps → `results/live/overhead.json`.

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

## Evidence-locked Leg 3 lite numbers (do not invent)

Protocol: `configs/experiment_lite_overhead.yaml` (5 min/condition, 1 rps, 300 requests/condition). Stack `faultlab` (eu-west-1). Destroyed after round.

| Condition | bytes/1000 req | traces | lat median ms | lat p95 ms |
|-----------|---------------:|-------:|--------------:|-----------:|
| full | 19 000 061 | 511 | 916.24 | 1026.61 |
| policy | 3 739 927 | 51 | 875.63 | 1064.99 |
| off | 1 251 573 | 0 | 917.98 | 1029.16 |

- **initial_eval** reduction_policy_vs_full = 0.803 (directional only; **not** the locked finals)  
- **final_1–3** reductions: **0.383 / 0.422 / 0.472** — all **fail** original ≥0.50; all **pass** amended ≥0.35  
- Learned lower bound: **median $4.23\times10^{5}$ bytes/1000 req** from $n{=}8$ RE2-OB subset (`results/live/learned_lower_bound.csv`)  
- Lite is **directional** measured evidence, not confirmatory 30-minute cells

## What is NOT done (soft)

1. Optional: full CausalRCA 90-case rerun (non-blocking; currently quarantined; ~minutes/case).
2. Optional: PDF rebuild after claim hygiene (pdflatex currently errors; over-length vs 20-page cap).
3. Full 90-case RCAEval parquet catalogue / 30-min Leg 3 cells. Learned-LB **subset** ($n{=}8$) is filled.

## Blockers to marketing-100

**None remediable at disclosed floor.** Soft packaging (CausalRCA 90 / clean PDF) is beyond-CA2. Original ≥0.50 fail + F1 gap are **evidenced negatives** (N-Yash dated WONTFIX), not inventable wins. **No AWS blocker.**

```
COMPLETE=yes ALIGNMENT=~72 CA2_FLOOR=met
INITIAL_EVAL_PASS=yes FINAL3=done_3of3
READY_FOR_AWS=yes SOLE_AWS_RESIDUAL=closed AWS_CLASS=required
LITE_PREP=yes LITE_APPLIED=yes LITE_DESTROYED=yes LIVE_OVERHEAD_EVIDENCE=yes
LEARNED_LB_SUBSET=yes LIVE_INITIAL_EVAL_1=yes
MOVE_ALLOWED=yes AUDIT_LEG3=EXIT0
REDUCTION_050=FAIL REDUCTION_035_AMENDED=PASS
```
