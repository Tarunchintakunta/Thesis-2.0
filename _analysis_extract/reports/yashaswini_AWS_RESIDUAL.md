# Yashaswini alignment residual (AWS-goal → sole-AWS ready)

**Updated:** 2026-09-20 (lite Leg 3 **executed + destroyed**)  
**Alignment after live lite Leg 3:** **~96/100** (was ~88% after claim hygiene; was ~75% baseline)  
**Live Leg 3:** **closed** — measured `results/live/overhead.json`

## Compact
`RQ10 Obj14 Method12 Impl14 Exp14 Metrics10 Evidence12 Claims9 Rubric5` → **~96/100**

## Hygiene / non-AWS work done
- `evaluation.tex` Leg 2 tables locked to `results/rcaeval/*` (AC@3=0.611, F1=0.469)
- CausalRCA **quarantined** as non-peer: $n{=}4$ + `fixed_order.json` share$=1.0$ (not an AWS blocker)
- `yashaswini_final_report.md` rewritten; invented competitiveness withdrawn
- Intro Leg 2/3 wording corrected; latex `refs.bib` synced from verified artefact bib (DOI notes)

## Live Leg 3 (this round) — DONE

| Check | Result |
|-------|--------|
| Protocol | Lite — `configs/experiment_lite_overhead.yaml`: 5 min × 3 @ 1 rps (300 req/condition) |
| Stack | Terraform `name_prefix=faultlab` (avoided `sflad-*` orphan collision) |
| Tags | `project` / `managed_by` / `purpose` / `data` only |
| Evidence | `results/live/overhead.json`; raw `data/runs/live_lite_overhead/` |
| reduction_policy_vs_full | **0.803** (≥0.5) — measured |
| Destroy | **yes** — 26 resources destroyed after round |
| Invented metrics | **none** |

### Measured summary (evidence-locked)

| Condition | bytes/1000 | traces | median ms | p95 ms |
|-----------|----------:|-------:|----------:|-------:|
| full | 1.900e7 | 511 | 916.24 | 1026.61 |
| policy | 3.740e6 | 51 | 875.63 | 1064.99 |
| off | 1.252e6 | 0 | 917.98 | 1029.16 |

Cost $/M req (from measured volumes × `configs/prices.yaml`): full ≈ 10.93, policy ≈ 2.25.  
Learned lower bound column: null (RCAEval parquet absent on runner) — disclosed, not invented.

## Sole hard residual to 100%
**None (AWS).** Soft only: optional CausalRCA 90; optional PDF; optional learned-LB parquet / full 30-min cells.

**AWS residual:** **no** — Leg 3 lite closed

```
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=closed READY_FOR_AWS=yes
LITE_PREP=yes LITE_APPLIED=yes LITE_DESTROYED=yes LIVE_OVERHEAD_EVIDENCE=yes
ALIGNMENT_ESTIMATE=~96/100
BLOCKER=none_aws
```
