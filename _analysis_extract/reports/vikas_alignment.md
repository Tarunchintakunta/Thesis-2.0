# Vikas alignment residual (formal CA2)

**Scope:** `vikas-thesis/` + formal `VikasReddyAmanagantti_X25178849_proposal.docx`  
**Updated:** 2026-09-21  
**Alignment to formal CA2:** **~74/100** (was incorrectly scored **100** on the scoreboard while live full campaign was empty)

## Compact
`RQ8 Obj8 Gap9 Method13 Impl13 Exp5 Claims9 Rubric soft9` → **~74/100**

## Working-tree evidence (verified)

| Evidence | Path | Fact |
|----------|------|------|
| Live pilot | `data/runs/live/pilot/deliveries.jsonl` | **300 lines** / 157055 bytes; `run_info.json` 2026-09-19 eu-west-1 |
| Pilot sizing | `results/live/pilot_choice.json` | **N=1000** (binding: P2 latency req 392) |
| Live campaign deliveries | `data/runs/live/campaign/deliveries.jsonl` | **0 bytes** — not executed |
| Campaign schedule / GT | `campaign/schedule.csv`, `ground_truth.jsonl` | Prepared (9000 GT rows); no deliveries |
| campaign_r2 / campaign_r3 | `run.log` only | Start lines only (`start pid=…`); **no** deliveries |
| Moto | `results/moto/` | Functional plumbing only — **not** AWS RQ answer |
| Live analysis cells | `results/live/` | pilot_* only; **no** campaign `summary.md` / cells / figures |
| P4 / TransactWrite | ASSUMPTIONS A12 + STATUS | **Out of scope** (quarantined) |

**No finished campaign found** in-tree or to harvest. Do **not** invent campaign results.

## Formal CA2 commitments vs delivery

| Commitment | Status |
|------------|--------|
| RQ: P2/P3 vs P1 duplicate mutation under injected Lambda retries + latency/capacity cost | Framed; **factorial AWS answer unmet** |
| Obj1–4 (dup rate × {1,2,5}; latency/capacity; control behaviour; correctness–cost surface) | Partial Obj1 via pilot (mult=2) + moto; **Obj2–4 AWS unmet** |
| Pilot ≈50/path → set N → full campaign with 95% CIs + Holm | Pilot **done**; campaign **empty** |
| Stock Lambda + DynamoDB; P1/P2/P3 only | Artefact + IaC present |
| Halfmoon as criterion contrast (no custom runtime) | Report hygiene OK |

## Why not 100%

CA2 **evaluation scope** requires the live full campaign (pilot-chosen N × 3 paths × 3 multiplicities) with CIs and pre-registered tests. Empty `deliveries.jsonl` means that scope is unmet. Pilot ≠ campaign. Moto ≠ AWS.

## Blockers to 100%

1. **Hard / sole:** run + analyse live full campaign → non-empty `campaign/deliveries.jsonl` + `results/live/` cells/figures; fold into Evaluation.
2. Soft: DOI `note={doi:}` hygiene; conclusion still pending campaign cells.

```
ALIGNMENT=~74 COMPLETE=no SOLE_AWS_RESIDUAL=yes BLOCK_FULL_EVAL=yes
PILOT=done CAMPAIGN=empty READY_FOR_AWS=yes (sole residual is the campaign)
```

Vikas Reddy Amanagantti
