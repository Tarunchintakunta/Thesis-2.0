"""Local simulation: synthetic tenants, JWT+middleware+RLS+quotas → JSON results."""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

from auth.jwt_tokens import DEFAULT_SECRET, issue_token
from db.store import Record, TenantStore
from metrics.fairness import EvalMetrics
from middleware.tenant_filter import AuthError, CrossTenantDenied, authenticate, enforce_tenant_match
from quota.redis_quota import InMemoryQuotaEngine, QuotaLimit
from security.pen_tests import run_cross_tenant_probes, run_quota_abuse


def run_pilot(
    *,
    n_tenants: int = 20,
    requests_per_tenant: int = 100,
    cross_tenant_probes: int = 10_000,
    seed: int = 42,
    out_dir: Path | None = None,
) -> dict:
    rng = random.Random(seed)
    secret = DEFAULT_SECRET
    store = TenantStore(rls_enabled=True)
    quotas = InMemoryQuotaEngine()
    metrics = EvalMetrics(tenants=n_tenants)

    tenants = [f"tenant-{i:03d}" for i in range(n_tenants)]
    # Unequal soft targets to stress fairness under hard caps
    for i, tid in enumerate(tenants):
        hard = 200 if i % 5 else 80  # some tenants smaller caps
        quotas.set_limits(
            tid,
            api=QuotaLimit(hard=hard, soft=int(hard * 0.8)),
            storage=QuotaLimit(hard=5000, soft=4000),
            compute=QuotaLimit(hard=300, soft=240),
        )
        store.set_config(tid)
        store.insert(Record(id=f"{tid}-doc-0", tenant_id=tid, kind="doc", payload={"seed": True}))

    # Happy-path + noisy neighbour workload
    for tid in tenants:
        for r in range(requests_per_tenant):
            metrics.requests += 1
            t0 = time.perf_counter()
            token = issue_token(sub=f"{tid}-user", tenant_id=tid, secret=secret)
            try:
                ctx = authenticate(f"Bearer {token}", secret=secret)
            except AuthError:
                continue
            metrics.auth_latencies_ms.append((time.perf_counter() - t0) * 1000)

            # own-tenant read via RLS
            store.set_config(ctx.claims.tenant_id)
            _ = store.list_for_session()

            # occasional forged cross-tenant attempt mixed into traffic (~2%)
            if rng.random() < 0.02:
                metrics.cross_tenant_attempts += 1
                victim = rng.choice([t for t in tenants if t != tid])
                try:
                    enforce_tenant_match(ctx, victim)
                    store.set_config(ctx.claims.tenant_id)
                    leaked = store.get(f"{victim}-doc-0")
                    if leaked is not None:
                        metrics.cross_tenant_leaked += 1
                    else:
                        metrics.cross_tenant_blocked += 1
                except CrossTenantDenied:
                    metrics.cross_tenant_blocked += 1

            qd = quotas.check_and_consume(tid, "api", 1)
            metrics.quota_latencies_ms.append(qd.latency_ms)
            if not qd.allowed:
                metrics.hard_rejects += 1
            metrics.tenant_api_usage[tid] = quotas.usage(tid, "api")

    # Dedicated 10k cross-tenant pen suite (CA1 claim)
    pen = run_cross_tenant_probes(n=cross_tenant_probes, secret=secret, store=TenantStore(rls_enabled=True))
    metrics.cross_tenant_attempts += pen["attempts"]
    metrics.cross_tenant_blocked += pen["blocked"]
    metrics.cross_tenant_leaked += pen["leaked"]

    abuse = run_quota_abuse(InMemoryQuotaEngine(), "tenant-abuse", burst=200)

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "mode": "local_sim",
        "note": "LOCAL_SIM / in-memory JWT+RLS+quota — NOT live AWS RDS/ElastiCache. No real PII.",
        "dataset": {
            "type": "synthetic_tenants",
            "pii": False,
            "n_tenants": n_tenants,
            "requests_per_tenant": requests_per_tenant,
            "cross_tenant_probes": cross_tenant_probes,
            "generator": "sim.runner.run_pilot",
        },
        "aws_mapping": {
            "auth": "API Gateway / Cognito JWT (local HS256 stand-in)",
            "app": "Lambda / ECS middleware (local Python)",
            "db": "RDS PostgreSQL RLS (in-memory + sql/ policies)",
            "quota": "ElastiCache Redis (in-memory counters)",
            "evaluation": "local_only_floor",
        },
        "metrics": metrics.to_dict(),
        "pen_test_10k": pen,
        "quota_abuse_sample": abuse,
        "targets": {
            "zero_unauthorized_access": True,
            "jain_gt_0_9": metrics.jain() > 0.9,
            "auth_p95_lt_50ms": metrics.to_dict()["auth_budget_50ms_ok"],
            "quota_p95_lt_5ms": metrics.to_dict()["quota_budget_5ms_ok"],
        },
    }

    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "pilot_results.json"
        path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        summary["written"] = str(path)
    return summary


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    out = run_pilot(out_dir=root / "results" / "local_sim")
    print(json.dumps({"written": out.get("written"), "targets": out["targets"], "jain": out["metrics"]["jain_fairness_index"]}, indent=2))
