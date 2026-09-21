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

## Venkat exploration note (this run)
- Report: `_analysis_extract/reports/venkat_alignment.md`
- AWS_CLASS=required (EC2 matched-vCPU)
- GATE_READY=yes for exploration completeness (not 100% CA2 alignment)
- SOLE_AWS_RESIDUAL=yes (**multi-instance `da.matmul` + eval sync**; round-1 saved; no invented matmul timing)
- Alignment (explore): **63%** (live evidence folded into STATUS/LaTeX/residual; still <100%)
- Residual: `_analysis_extract/reports/venkat_AWS_RESIDUAL.md` (`READY_FOR_AWS=yes`)
- Live: `results/live/ec2_round1_summary.json` — 1× t3.small vs 2× t3.micro; scale-up ~0.0067s; on-node ~0.52s; multi-instance matmul **timed_out**
- Note: Terraform defaults already t3.small / t3.micro / count=2; fleet destroyed after round-1

## LIVE (READY subset) — 2026-09-20 / corrected 2026-09-21
- Vikas: campaign **not** finished — working-tree `campaign/deliveries.jsonl` is **0 bytes** (r2/r3 = `run.log` start only). Alignment **~74%**; sole residual = full campaign. See `vikas_AWS_RESIDUAL.md`.
- Chaitanya: python Init Duration live cells collected (`data/processed/live/`)
- Runbook research: [Chaitanya live Init path](bc-6db36ab1-f0a4-55ec-8e5c-1889de8454b8) (superseded by applied TF + live round)

- Report: `_analysis_extract/reports/yashaswini_alignment.md`
- AWS_CLASS=required (Lambda, API Gateway, DynamoDB, CloudWatch, X-Ray)
- GATE_READY=yes for exploration completeness (not 100% CA2 alignment)
- Agent: https://cursor.com/agents/bc-a96b5798-fe38-54b8-8582-39d4dec89f04
