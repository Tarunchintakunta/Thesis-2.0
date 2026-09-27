# Baseline paper (CA1/CA2-aligned)

**Student folder:** `pavan`  
**Thesis:** Tenant-aware enforcement in multi-tenant SaaS (JWT + middleware + PostgreSQL RLS + Redis quotas)  
**Artefact:** `tenant-aware-enforcement/`  
**Selection rule:** Maximize Baseline→CA gap within **Mar 2025–Sep 2026**.

## Primary baseline

**Citation:** Cheng, A., Kabcenell, A., Shi, X., Huey, J., Bailis, P., Crooks, N. and Stoica, I. (2025) ‘Fair Transaction Processing for Multi-Tenant Databases’, *Proceedings of the VLDB Endowment*, 18(8), pp. 2602–2615.  
**DOI:** `10.14778/3742728.3742751`  
**File:** `PRESENT: Cheng_et_al_2025_Fair_Txn_VLDB_baseline.pdf`  
**OA URL:** https://www.vldb.org/pvldb/vol18/p2602-cheng.pdf

| Field | Baseline (Cheng et al. 2025 / DRFT) | Maps to this thesis |
|-------|--------------------------------------|---------------------|
| **Problem** | Multi-tenant DB tenants starve each other under unfair txn scheduling | Noisy-neighbour + cross-tenant risk in shared SaaS |
| **Solution** | Fair transaction scheduler (share guarantees + strategy-proofness) inside the DB engine | **End-to-end** tenant context: JWT claims → app middleware → PostgreSQL RLS → Redis multi-dimensional quotas |
| **Gap** | Fairness at **txn scheduling** layer; does **not** provide JWT tenant claims, ORM middleware filtering, RLS policies, or Redis API/storage/compute quotas with auth latency budgets | **Their gap is our problem** |
| **Metrics** | Fairness / share guarantees / throughput under contention | **Retain** fairness (Jain’s index); **add** zero cross-tenant unauthorized access, auth latency &lt;50ms, quota overhead &lt;5ms |

**Baseline→CA alignment:** ~**80%** (same multi-tenant fairness concern; different enforcement stack).

## Why keep Cheng (CA1-named) as primary?

- Recency: VLDB 2025 — **PASS** for Mar 2025–Sep 2026 window.  
- Peer-reviewed PVLDB.  
- Named in CA1; clear residual gap for JWT+middleware+RLS+Redis quotas.  
- OA PDF obtained.

## Related (secondary OA)

**Wang et al. (2025)** ‘Zero-trust based dynamic access control for cloud computing’, *Cybersecurity*, 8, art. 12. DOI `10.1186/s42400-024-00320-x`.  
**File:** `Wang_et_al_2025_ZeroTrust_Access_Control.pdf`  
Supports zero-trust / continuous verification language for JWT path; not primary because it lacks RLS+quota fairness ablation.

## Recency / relevance verdict
- **Recency:** PASS (2025 VLDB). **Relevance:** HIGH (multi-tenant fairness). **Gap:** CLEAR (DB scheduler ≠ end-to-end tenant-aware enforcement).
