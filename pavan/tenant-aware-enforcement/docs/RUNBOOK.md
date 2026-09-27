# RUNBOOK — tenant-aware-enforcement

## Floor

1. `make setup && make test && make pilot`
2. Confirm `results/local_sim/pilot_results.json` has `mode: local_sim` and `zero_unauthorized_access: true`.
3. Do not present local JWT/HS256 timings as Cognito/API Gateway SLOs.

## Optional docker

1. `make docker-up` — Postgres on 54329, Redis on 63799; RLS SQL applied.
2. Wire a live client later; floor does not require it.
3. `make docker-down` when finished.

## Penetration probes (ethics)

Only against synthetic tenants on researcher-controlled local process. No third-party systems. Dual-use details stay high-level (ISO/IEC 29147 spirit).

## AWS live (future)

RDS Postgres RLS + ElastiCache Redis + API Gateway JWT authorizer on student account; destroy after; no secrets in git.
