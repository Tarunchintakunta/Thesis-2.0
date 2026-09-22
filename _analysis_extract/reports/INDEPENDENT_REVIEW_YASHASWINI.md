# Independent review — Yashaswini (serverless-fault-localisation)

**Date:** 2026-09-22  
**STATUS claim overturned:** `ALIGNMENT=100` / reduction_policy_vs_full=0.803 as locked — **not accepted**.  
**Honest CA2 floor:** **partial (~68)**

## RQ (CA2 / master prompt)
> What accuracy–overhead position does rule-based fault detection and localisation occupy relative to learned deep baselines in AWS serverless microservices?

Pre-committed decision rule: F1 within 10 pp of strongest reproducible baseline **and** telemetry volume ≥50% reduced.

## Artefact reality
SAM/Terraform `faultlab` + RCAEval Leg 2 + lite Leg 3 overhead runner. CausalRCA n=4 quarantined (`fixed_order.json` share=1.0).

## Evidence (disk)

| Claim | Verdict | Path / numbers |
|-------|---------|----------------|
| Leg 2 localisation | **Demonstrated** | `results/rcaeval/localisation.csv`: rules n=90 AC@1=0.289 AC@3=**0.611**; CIRCA AC@3=0.878; BARO AC@3=0.878; hybrid AC@3=0.478 |
| Rule detection F1 | **Demonstrated (weak)** | `detection.json`: F1=**0.46875**, precision=0.306, recall=1.0 — gap to Xing 0.938 = **46.9 pp** (decision rule fails) |
| Live overhead ≥50% cut | **Partial → fail on finals** | `initial_eval_1/overhead.json`: reduction=**0.803** (meets). `final_1|2|3/overhead.json`: **0.383 / 0.422 / 0.472** — **all miss** expected 0.5. Root `results/live/overhead.json` = final_1 (0.383) |
| STATUS “19 000 061 / 0.803 locked” | **Claimed / stale** | Only true for `initial_eval_1`; STATUS table ignores failing finals |
| Learned LB | **Demonstrated (subset)** | `learned_lower_bound.csv` n=8; median **4.23e5** bytes/1000 — parquet lower bound, not live service |

## Floor
**Partial.** Joint accuracy–overhead RQ is only half-answered: Leg 2 is real; Leg 3 measured but **pre-committed ≥50% cut fails on 3/3 finals**; F1 not within 10 pp of Xing or of CIRCA/BARO peers.

## Highest-value next steps
1. Re-tune sampling policy until ≥3 live rounds clear 0.50 reduction — or rewrite decision rule to match measured 0.38–0.47.  
2. Quarantine STATUS 0.803 as initial-only; cite final distribution.  
3. Optional: 30-min cells only after policy meets rule.
