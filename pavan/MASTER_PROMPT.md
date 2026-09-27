# MASTER PROMPT / CA COMMITMENTS — Pavan Sai Bodduluru (X24211371)

## Identity

| Field | Value |
|-------|-------|
| Name | Pavan Sai Bodduluru |
| Student ID | X24211371 |
| Programme | MSc Cloud Computing, NCI |
| Artefact | `pavan/tenant-aware-enforcement/` |

## Research question

How can a unified tenant-aware framework integrate JWT tenant/role claims, application middleware filtering, PostgreSQL RLS, and Redis multi-dimensional quotas to achieve zero unauthorized cross-tenant access, Jain fairness &gt; 0.9, authentication latency &lt; 50 ms, and quota overhead &lt; 5 ms?

## Mechanisms

1. JWT with `tenant_id` + `role` claims  
2. Middleware enforce + ORM-style row filter  
3. Shared-schema PostgreSQL RLS (`app.current_tenant`)  
4. Redis atomic multi-dim quotas (api / storage / compute)  

## Metrics

- Cross-tenant unauthorized access count (target 0 / 10k probes)  
- Jain’s fairness index (target &gt; 0.9)  
- Auth latency p95 (&lt; 50 ms)  
- Quota check latency p95 (&lt; 5 ms)  

## Baseline

Cheng et al. (2025) PVLDB DOI `10.14778/3742728.3742751` — fair txn scheduling.  
Gap: scheduler ≠ end-to-end JWT+middleware+RLS+Redis quotas.

## Dataset / ethics

Synthetic tenants only; no PII; probes only on local researcher-controlled process.

## Non-negotiables

No fabricated live AWS numbers; no secrets in git; prefer local/docker floor.
