# Tenant-Aware Enforcement in Multi-Tenant SaaS — Draft report

**Author:** Pavan Sai Bodduluru (X24211371)  
**Status:** Draft aligned to LOCAL_SIM evidence (not live AWS)

## Abstract

Multi-tenant SaaS must stop cross-tenant leakage and noisy neighbours. This project integrates JWT tenant claims, application middleware, PostgreSQL-style RLS, and Redis multi-dimensional quotas. A local simulator with 10,000 cross-tenant probes reports zero unauthorized access, Jain fairness ≈0.99, and auth/quota latencies well under CA budgets. Live RDS/ElastiCache confirmation remains future work.

## 1. Introduction

Problem: fragmented auth, DB isolation, and quotas. RQ as in MASTER_PROMPT. Contribution: unified local artefact + ablation-ready AWS mapping.

## 2. Baseline

Cheng et al. (2025) VLDB fair transaction processing (DOI 10.14778/3742728.3742751) improves multi-tenant DB fairness at the scheduler. Gap: does not deliver end-to-end JWT→middleware→RLS→Redis quota enforcement with security probe metrics. Wang et al. (2025) zero-trust access control kept as related OA.

## 3. Method

Design-science + controlled probes. Synthetic tenants. Metrics: unauthorized access, Jain index, auth/quota latency. Floor = in-memory; optional docker Postgres+Redis; SQL RLS policies shipped.

## 4. Design

Artefact `tenant-aware-enforcement/`: JWT, middleware, RLS store, quota engine, pen-test harness, docker-compose, Terraform stubs.

## 5. Evaluation (LOCAL_SIM)

Pilot: 20 tenants × 100 requests + 10k probes → 0 leaks; Jain≈0.993; auth p95≈0.01 ms; quota p95≪5 ms (in-memory — not AWS). Label: local_sim only.

## 6. Conclusions

Defence-in-depth tenant context stops cross-tenant reads in local tests; quotas enforce hard caps and high Jain under the pilot workload. Next: docker RLS integration tests and student-account AWS mapping with destroy-after-run.

## References (selected)

Cheng et al. (2025) DOI 10.14778/3742728.3742751; Wang et al. (2025) DOI 10.1186/s42400-024-00320-x; GDPR; ISO/IEC 27001:2022; NIST SP 800-63B; NIST SP 800-207.
