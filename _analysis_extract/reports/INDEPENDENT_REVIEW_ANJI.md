# Independent review — Anji (sqs-reliability-recovery)

**Date:** 2026-09-22  
**STATUS claim overturned:** `CA2_ALIGNMENT=100` / `COMPLETE=yes` — **not accepted**.  
**Honest CA2 floor:** **partial (~72)**

## RQ (CA2 / master prompt)
> How does Amazon SQS configuration affect message reliability and recovery under injected consumer and downstream failures?

Objectives require VT / MRC / DLQ effects on loss+dup; recovery time; Kyrychenko guidance-under-fault; reliability–recovery–cost trade-off. H1–H3 with Holm–Bonferroni.

## Artefact reality
Real stack: SAM + Terraform SQS/Lambda/DLQ/Dynamo + localsim + live runner under `anji-thesis/sqs-reliability-recovery/`. Live backend cells exist with `backend: live`.

## Evidence (disk)

| Claim | Verdict | Path / numbers |
|-------|---------|----------------|
| Localsim confirmatory H1–H3 | **Demonstrated (null)** | `results/summary/stats_H1_H2_H3.json`: `runs=350`, `backend=["localsim"]`. H1 no variance (all loss=0); H2 KW p=0.489 → p_adj=1; H3_loss no variance; H3_recovery MW p=0.021 → p_adj=0.084 — **all fail to reject** |
| Live AWS lite key-cells | **Demonstrated (smoke)** | `results/live/{key_cells,initial_eval_1,final_1,final_2,final_3}/` — each 4×n=1. initial_eval_1: loss=0 all; MRC1 DLQ=0.23 success=0.805; VT30 recovery=3.123s vs VT90=2.609s (not monotone); wall=793.0s; usd≈$0.00132 |
| Live confirmatory n>1 / Holm | **Not met** | STATUS itself: `LIVE_CONFIRMATORY=not_run` |
| Full CA2 IV matrix live (batch, burst, multi-fault) | **Claimed / not on live** | Live config = 4 cells only |
| Final-3 as independent confirmatory | **Partial** | Packs exist (`summary.csv`); still n=1 smoke; run_ids config-hashed |

## Floor
**Partial.** Artefact + live smoke answer the RQ directionally (loss=0; MRC1 DLQ capture 0.155–0.23). Confirmatory statistics are localsim-only and **uniformly non-significant**; live does not recover VT→recovery law.

## Highest-value next steps
1. Live n≥3 on the 4 key cells (`configs/live_key_cells_n3.yaml`) with destroy-after.  
2. Stop citing H1–H3 as supporting effects — report nulls honestly.  
3. One beyond-smoke campaign that varies recovery DV with measurable variance.
