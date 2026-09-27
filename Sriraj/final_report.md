# Serverless Webhook Processing with Retry, DLQ, and Idempotency — Draft report

**Author:** Sriraj Gannavaram (x23431873)  
**Programme:** MSc Cloud Computing, National College of Ireland  
**Status:** Draft aligned to LOCAL_SIM evidence (not live AWS)

## Abstract

Webhook-driven integrations fail under transient faults, duplicates, and poison messages. This project implements an integrated serverless-style pipeline with exponential-backoff retry and jitter, dead-letter queue capture/replay, and Redis-like idempotency, evaluated under controlled fault injection at 0–50%. A local simulator (stand-in for AWS Lambda + SQS + ElastiCache) shows large delivery-success gains from B→R→RD/RDI and perfect duplicate suppression under RDI, with modest happy-path latency overhead. Live AWS confirmation remains future work.

## 1. Introduction

Research problem: serverless webhook consumers face at-least-once delivery without built-in exactly-once semantics.  
RQ: To what extent does integrated retry + DLQ + idempotency improve reliability under faults?  
Contribution: joint B/R/RD/RDI ablation, Terraform stubs, open local harness.

## 2. Related work / baseline

**Primary baseline:** Qi et al. (2025), *Efficient Fault Tolerance for Stateful Serverless Computing with Asymmetric Logging*, ACM TOCS, DOI 10.1145/3725985. Halfmoon provides log-optimal exactly-once for stateful FaaS via asymmetric logging, but does not evaluate webhook HMAC ingestion, SQS backoff+DLQ replay, or Redis TTL idempotency as an integrated application stack under controlled fault rates.  
**Related:** Zhang et al. (2025) TOSEM failure-diagnosis survey (method language for controlled faults); Shafiei/Wen serverless surveys; Golec cold-start review.

## 3. Method

Design-science + controlled experiment. Configs B, R, RD, RDI × fault rates 0/10/25/50%. Synthetic payloads. Metrics: delivery success, duplicate suppression, latency percentiles, DLQ recovery. Floor = in-memory simulator; IaC stubs map to API Gateway, SQS, Lambda, ElastiCache.

## 4. Design & implementation

Artefact `webhook-reliability-eval/`: HMAC verify, backoff+full jitter, SQS/DLQ model, idempotency store, fault injector, pilot runner, pytest, Terraform SQS+DLQ stubs.

## 5. Evaluation (LOCAL_SIM)

Pilot `results/local_sim/pilot_results.json` (200 events/cell, duplicate_rate=0.10):

- At 50% fault: B success ≈0.57; R ≈0.94; RD/RDI ≈1.00 after DLQ replay.  
- RDI duplicate suppression ratio = 1.0 when duplicates injected.  
- Happy-path P50 rises slightly B→RDI (~2.5→~3.2 sim-ms), consistent with small bookkeeping/Redis overhead (RQ3 direction).  

**Label:** not live AWS. External validity limited to simulator fidelity.

## 6. Conclusions

Integrated RDI dominates baseline under faults in local simulation; DLQ enables recovery; idempotency stops duplicate side effects. Next: Terraform-complete live campaign on student AWS with destroy-after-run, then confirmatory statistics.

## References (selected)

Qi et al. (2025) DOI 10.1145/3725985; Zhang et al. (2025) DOI 10.1145/3715005; Shafiei et al. (2022); Wen et al. (2023); Golec et al. (2024); Jia & Witchel (2021); Barcelona-Pons et al. (2022).
