# MASTER PROMPT / CA2 COMMITMENTS — Sriraj Gannavaram (x23431873)

## Identity

| Field | Value |
|-------|-------|
| Name | Sriraj Gannavaram |
| Student ID | x23431873 |
| Programme | MSc Cloud Computing, NCI |
| Artefact | `Sriraj/webhook-reliability-eval/` |

## Research question

To what extent does an integrated retry, dead-letter queue, and idempotency framework enhance reliability in serverless webhook processing under faults?

### Sub-questions

- **RQ1:** Delivery success uplift of RDI vs B at fault rates 10%, 25%, 50%.
- **RQ2:** Duplicate suppression ratio of Redis idempotency at duplicate injection 5–20% (pilot uses 10%).
- **RQ3:** Happy-path latency overhead (P50/P95/P99) of the integrated framework.

## Factors (IVs)

| Factor | Levels |
|--------|--------|
| Reliability config | B, R, RD, RDI |
| Fault injection rate | 0, 0.10, 0.25, 0.50 |
| Duplicate injection | default 0.10 |

## Metrics (DVs)

1. Delivery success rate  
2. Duplicate suppression ratio  
3. Latency P50 / P95 / P99  
4. DLQ recovery rate  

## Architecture (CA2)

1. API Gateway HMAC-SHA256 ingestion  
2. SQS exponential-backoff retry + full jitter  
3. DLQ capture + replay  
4. Redis (ElastiCache) idempotency TTL keys  
5. Terraform IaC  
6. Controlled fault injection  

## Baseline

**Qi et al. (2025)** Halfmoon — ACM TOCS DOI `10.1145/3725985`.  
Gap: runtime asymmetric logging ≠ joint webhook retry+DLQ+Redis idempotency under fault injection.  
Zhang et al. (2025) TOSEM kept as related (outside primary recency window).

## Dataset

Synthetic webhook payloads only; no PII; generator `sim.runner.make_event`.

## Non-negotiables

- No fabricated live AWS numbers.  
- No AWS secrets in git.  
- Prefer local/moto floor; live apply only with student account + destroy.  
