# tenant-aware-enforcement

**Student:** Pavan Sai Bodduluru (X24211371)  
**Thesis:** Tenant-aware enforcement in multi-tenant SaaS  
**Floor:** LOCAL_SIM (in-memory JWT + RLS-style store + Redis-like quotas). Optional `docker compose` for Postgres 16 + Redis 7.

## Research question (CA1)

How can a unified tenant-aware framework integrate JWT tenant claims, middleware query filtering, PostgreSQL RLS, and multi-dimensional Redis quotas to achieve zero unauthorized cross-tenant access, Jain fairness &gt; 0.9, auth &lt; 50 ms, and quota overhead &lt; 5 ms?

## Quick start

```bash
cd tenant-aware-enforcement
make setup && make test && make pilot
# optional:
# make docker-up   # applies sql/rls_policies.sql
```

## Layout

| Path | Role |
|------|------|
| `src/auth/` | JWT issue/verify with `tenant_id` + role claims |
| `src/middleware/` | Bearer auth + cross-tenant deny + row filter |
| `src/db/` | RLS-style shared-schema store (+ SQLite helper) |
| `src/quota/` | Multi-dim atomic counters (api/storage/compute) |
| `src/security/` | Synthetic cross-tenant / quota-abuse probes |
| `sql/rls_policies.sql` | Real PostgreSQL RLS for docker/live |
| `docker-compose.yml` | Postgres 16 + Redis 7 |
| `results/local_sim/` | Committed LOCAL_SIM JSON |

## Dataset

Synthetic tenants (`tenant-000` …) and documents. **No PII.**

## Baseline

Cheng et al. (2025) VLDB fair txn processing — DOI `10.14778/3742728.3742751`.  
Gap: DB scheduler fairness ≠ end-to-end JWT+middleware+RLS+Redis quotas.

## Honest scope

Local numbers are **not** live RDS/ElastiCache/API Gateway measurements. AWS mapping documented; live apply future.
