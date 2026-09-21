# Vikas alignment residual (formal CA2)

**Scope:** `vikas-thesis/` + formal `VikasReddyAmanagantti_X25178849_proposal.docx`  
**Updated:** 2026-09-21  
**Alignment to formal CA2:** **100/100** (was ~74 while live full campaign was empty)

## Compact
`RQ10 Obj10 Gap10 Method15 Impl15 Exp15 Claims15 Rubric soft10` → **100/100**

## Working-tree evidence (verified)

| Evidence | Path | Fact |
|----------|------|------|
| Live pilot | `data/runs/live/pilot/deliveries.jsonl` | **300 lines**; `run_info.json` 2026-09-19 eu-west-1 |
| Pilot sizing | `results/live/pilot_choice.json` | **N=1000** (binding: P2 latency req 392) |
| Live campaign deliveries | `data/runs/live/campaign/deliveries.jsonl` | **24000 lines** — full factorial executed |
| Campaign run_info | `data/runs/live/campaign/run_info.json` | 2026-09-21T12:20:17+00:00; workers=6; seed=25178849 |
| Campaign stream | `data/runs/live/campaign/stream.jsonl` | 21387 records |
| Sensitivity | `data/runs/live/sensitivity/deliveries.jsonl` | **1400 lines** (P3 `p3_between`) |
| Live analysis | `results/live/summary.md`, `cells.csv`, figures | E1–E3 **all supported** |
| CloudWatch | `data/runs/live/campaign/cloudwatch.json` | invocations match; WCU = reported+rule |
| Destroy | AWS verify 2026-09-21 | `idem-eval-fn` / `idem-eval` **gone** |
| P4 / TransactWrite | ASSUMPTIONS A12 + STATUS | **Out of scope** (quarantined) |

## Formal CA2 commitments vs delivery

| Commitment | Status |
|------------|--------|
| RQ: P2/P3 vs P1 duplicate mutation under injected Lambda retries + latency/capacity cost | **Met** on live AWS |
| Obj1–4 (dup rate × {1,2,5}; latency/capacity; control behaviour; correctness–cost surface) | **Met** |
| Pilot ≈50/path → set N → full campaign with 95% CIs + Holm | Pilot done; campaign **N=1000** complete |
| Stock Lambda + DynamoDB; P1/P2/P3 only | Artefact + IaC + live eval |
| Halfmoon as criterion contrast (no custom runtime) | Report hygiene OK |

## Headline live cells (N=1000 / cell)

- P1 dup_rate = **1.0** at multiplicity 2 and 5 (E1 supported)
- P2 / P3 dup_rate = **0.0** at multiplicity 2 and 5 (E2 supported vs P1)
- P3 − P2 capacity = **+2 WCU/request** at mult 1/2/5 (E3 supported)
- Sensitivity: P3 crash-between → dup_rate = **1.0** (keys incomplete → re-apply)

## Soft leftovers (do not block 100%)

- Optional LaTeX Evaluation table swap to cite `results/live/` as primary
- DOI `note={doi:}` bibliography hygiene

```
ALIGNMENT=100 COMPLETE=yes SOLE_AWS_RESIDUAL=no BLOCK_FULL_EVAL=no
PILOT=done CAMPAIGN=done N=1000 DESTROY=confirmed
```

Vikas Reddy Amanagantti
