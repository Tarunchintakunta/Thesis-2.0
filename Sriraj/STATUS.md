# Sriraj Gannavaram — STATUS

**Updated:** 2026-09-27 (IST / Asia/Calcutta)  
**Student ID:** x23431873  
**Title:** Serverless Webhook Processing with Retry, Dead-Letter Queue, and Idempotency  
**Artefact:** `Sriraj/webhook-reliability-eval/`

## Gates

```
CA2_ALIGNMENT=yes
FLOOR_COMPLETE=yes
UNIT_TESTS=16_passed
LOCAL_PILOT=yes
LIVE_AWS=not_run
FINAL_REPORT=draft
BASELINE=Qi_et_al_2025_Halfmoon_TOCS
DESTROY_CONFIRMED=n/a_local_only
```

## Honest completion

| Item | Status | Evidence |
|------|--------|----------|
| RQ / configs B→R→RD→RDI / faults 10–50% | **aligned** | `MASTER_PROMPT.md`, `configs/experiment.yaml` |
| Baseline (recent peer-reviewed) | **done** | Qi et al. 2025 TOCS DOI `10.1145/3725985`; PDF in `baseline_papers/` |
| Artefact src (ingest, retry, dlq, idempotency) | **done** | `webhook-reliability-eval/src/` |
| pytest | **green** | 16 passed (2026-09-27) |
| Local pilot JSON | **committed path** | `results/local_sim/pilot_results.json` — **LOCAL_SIM, not live AWS** |
| Terraform | **stubs only** | SQS+DLQ module; Lambda/API GW/Redis not applied |
| Live AWS numbers | **none** | Do not fabricate |

## Local pilot snapshot (LOCAL_SIM only)

| Config | Fault 0% success | Fault 50% success | Dup suppress @0% | P50 ms @0% |
|--------|-----------------:|------------------:|-----------------:|-----------:|
| B | 1.000 | 0.565 | n/a (no idem) | ~2.5 |
| R | 1.000 | 0.935 | n/a | ~2.8 |
| RD | 1.000 | 1.000 | n/a | ~2.8 |
| RDI | 1.000 | 1.000 | 1.000 | ~3.2 |

Direction matches CA2 hypotheses (RDI ≫ B under faults; idempotency suppresses duplicates; small happy-path latency overhead). **These are simulator effect directions, not AWS production SLOs.**

## One-liner

**FLOOR COMPLETE:** runnable local artefact + green tests + Qi et al. 2025 baseline gap documented; evaluation is LOCAL_SIM only (no live AWS).
