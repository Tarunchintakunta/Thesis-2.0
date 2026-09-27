# Baseline paper (CA2-aligned)

**Student folder:** `Sriraj`  
**Thesis:** Serverless webhook processing with retry, DLQ, and idempotency  
**Artefact:** `webhook-reliability-eval/`  
**Selection rule:** Maximize Baseline→CA2 fit (scope / variables / method / metrics) within **Mar 2025–Sep 2026**.

## Primary baseline

**Citation:** Qi, S., Feng, H., Liu, X. and Jin, X. (2025) ‘Efficient Fault Tolerance for Stateful Serverless Computing with Asymmetric Logging’, *ACM Transactions on Computer Systems*, 43(1–2), Article 3, pp. 1–43.  
**DOI:** `10.1145/3725985`  
**Online AM:** 28 March 2025 · **Published:** 9 June 2025  
**File:** `PRESENT: Qi_et_al_2025_Halfmoon_TOCS_baseline.pdf` (author OA PDF)  
**OA URL:** https://tomquartz.github.io/files/TOCS25_AsymmLogging.pdf

| Field | Baseline (Halfmoon / Qi et al. 2025) | Maps to this thesis (CA2) |
|-------|--------------------------------------|---------------------------|
| **Problem** | Simple retry on stateful FaaS can corrupt shared state with duplicate updates; logging for exactly-once is expensive | Webhook FaaS pipelines also need exactly-once-ish behaviour under transient faults and at-least-once queues |
| **Solution** | Runtime asymmetric logging protocols (read- or write-logging) for log-optimal exactly-once semantics | **Application-level** stack: SQS exponential-backoff+jitter retry, DLQ capture/replay, Redis idempotency keys, HMAC ingestion |
| **Gap** | Runtime logging for stateful SSFs; **no** webhook HMAC path, **no** SQS/DLQ topology, **no** Redis TTL idempotency, **no** joint B→R→RD→RDI ablation under controlled fault rates | **Their gap is our problem:** integrate retry + DLQ + idempotency and measure marginal reliability under 10/25/50% faults |
| **Metrics** | Latency, logging overhead vs Boki | **Retain** latency (P50/P95/P99); **add** delivery success rate, duplicate suppression ratio, DLQ recovery |

**Baseline→CA2 alignment:** ~**82%** (same FaaS exactly-once / fault-tolerance concern; different layer and joint mechanisms).

## Why not the CA2-named Zhang et al. (2025) as primary?

**Citation:** Zhang, S. et al. (2025) ‘Failure Diagnosis in Microservice Systems: A Comprehensive Survey and Analysis’, *ACM TOSEM*, 35(1), Article 2. DOI `10.1145/3715005`.  
**File:** `Zhang_et_al_2025_Failure_Diagnosis_survey.pdf` (kept as related OA reference).

| Check | Verdict |
|-------|---------|
| Recency (Mar 2025–Sep 2026) | **FAIL as primary** — Online AM 23 Jan 2025 (outside the 6–7 month window for this pack) |
| Relevance | HIGH for **controlled fault / failure taxonomy** method language, but it is a **diagnosis survey**, not an implemented reliability stack |
| Gap fit | Advocates systematic failure experiments; does **not** implement or evaluate SQS retry+jitter + DLQ replay + Redis idempotency on serverless webhooks |

**Decision:** Keep Zhang as secondary/related (CA2 literature). Use **Qi et al. Halfmoon TOCS 2025** as the primary baseline because it is (a) inside the recency window, (b) peer-reviewed ACM TOCS, (c) OA PDF available, and (d) leaves a clear engineering gap this CA2 closes.

## Recency / relevance verdict
- **Recency:** PASS (Mar–Jun 2025). **Relevance:** HIGH (FaaS fault tolerance / exactly-once). **Gap:** CLEAR (runtime logging ≠ joint webhook retry+DLQ+idempotency under fault injection on AWS).
