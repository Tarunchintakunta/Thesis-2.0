# webhook-reliability-eval

**Student:** Sriraj Gannavaram (x23431873)  
**Thesis:** Serverless webhook processing with retry, DLQ, and idempotency  
**Floor evaluation:** **LOCAL_SIM** (in-memory SQS/DLQ + Redis-like store). Not live AWS.

## Research question

> To what extent does an integrated retry, dead-letter queue, and idempotency framework enhance reliability in serverless webhook processing under faults?

Configs: **B → R → RD → RDI**. Fault rates: **0 / 10 / 25 / 50%**. Metrics: delivery success, duplicate suppression, P50/P95/P99 latency, DLQ recovery.

## Quick start

```bash
cd webhook-reliability-eval
make setup
make test
make pilot
```

Results: `results/local_sim/pilot_results.json` (labelled `mode: local_sim`).

## Layout

| Path | Role |
|------|------|
| `src/ingestion/` | HMAC-SHA256 verify (API Gateway stand-in) |
| `src/retry/` | Exponential backoff + full jitter |
| `src/dlq/` | SQS + DLQ redrive + replay model |
| `src/idempotency/` | Redis-like SET NX EX store |
| `src/pipeline/` | Integrated B/R/RD/RDI processor |
| `src/fault/` | Controlled fault injection |
| `src/sim/` | Pilot runner → JSON |
| `terraform/` | IaC stubs (SQS+DLQ); live apply later |
| `configs/` | Experiment + per-mode YAML |

## Dataset

Synthetic webhook payloads only (`event_id`, `source`, `type`, `amount_cents`, …). **No PII.** Generator: `sim.runner.make_event`.

## Baseline

Qi et al. (2025) Halfmoon — ACM TOCS DOI `10.1145/3725985`. See `../baseline_papers/BASELINE_PAPER.md`.

## Honest scope

- Floor = local simulator + pytest green.
- Live AWS (API Gateway, Lambda, SQS, ElastiCache, Terraform apply) is **out of floor** until credentials + budget gate.
- Never commit AWS secrets.
