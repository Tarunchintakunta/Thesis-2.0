# Goal Exploration Gate — In-Scope Theses Only

**Goal:** AWS deploy/eval to 100% CA2 alignment  
**In scope:** Anji, Varun, Yashaswini, Rasool, Chaitanya, Vikas, Venkat, Nemi  
**Excluded:** Kasi (and mehak/pooja/uday/vishvaksen from AWS table)

## Exploration status (authoritative for gate)

| Thesis | Exploration report | Alignment (explore) | Gate |
|--------|-------------------|--------------------:|------|
| Nemi | Nemi_alignment.md | 44% | DONE |
| Chaitanya | chaitanya_alignment.md | 67% | DONE |
| Vikas | vikas_alignment.md | 68% | DONE |
| Anji | anji_alignment.md | 72% | DONE |
| Varun | varun_alignment.md | 58% | DONE |
| Yashaswini | yashaswini_alignment.md | 62% | DONE |
| Rasool | rassool_alignment.md | 62% | DONE |
| Venkat | venkat_alignment.md | 63% | DONE |

**Exploration gate: 8/8 DONE.**

**AWS deployment MUST NOT start until all 8 rows are DONE.** (Satisfied for exploration completeness; live apply still gated by per-thesis alignment / residual discipline.)

## Venkat exploration note (updated 2026-09-21)
- Report: `_analysis_extract/reports/venkat_alignment.md`
- AWS_CLASS=required (EC2 matched-vCPU) — **closed**
- GATE_READY=yes
- SOLE_AWS_RESIDUAL=**closed** (round-2 multi-instance `da.matmul` ok)
- Alignment: **100%** CA2 floor
- Residual: `_analysis_extract/reports/venkat_AWS_RESIDUAL.md` (`SOLE_AWS_RESIDUAL=closed`)
- Live: round-1 timed_out at n=500; round-2 matmul **0.2546 s**; initial_eval_1 matmul **0.2737 s** at n=250; fleets destroyed; INITIAL_EVAL_PASS=yes

## LIVE (READY subset) — 2026-09-20 / corrected 2026-09-21
- Vikas: campaign **not** finished — working-tree `campaign/deliveries.jsonl` is **0 bytes** (r2/r3 = `run.log` start only). Alignment **~74%**; sole residual = full campaign. See `vikas_AWS_RESIDUAL.md`.
- Chaitanya: python Init Duration live cells collected (`data/processed/live/`)
- Runbook research: [Chaitanya live Init path](bc-6db36ab1-f0a4-55ec-8e5c-1889de8454b8) (superseded by applied TF + live round)

- Report: `_analysis_extract/reports/yashaswini_alignment.md`
- AWS_CLASS=required (Lambda, API Gateway, DynamoDB, CloudWatch, X-Ray)
- GATE_READY=yes for exploration completeness (not 100% CA2 alignment)
- Agent: https://cursor.com/agents/bc-a96b5798-fe38-54b8-8582-39d4dec89f04
