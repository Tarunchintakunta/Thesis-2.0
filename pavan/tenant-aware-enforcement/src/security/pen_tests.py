"""Controlled adversarial probes (own synthetic tenants only — no real targets)."""
from __future__ import annotations

import time
from typing import Callable

from auth.jwt_tokens import issue_token
from db.store import Record, TenantStore
from middleware.tenant_filter import AuthError, CrossTenantDenied, authenticate, enforce_tenant_match
from quota.redis_quota import InMemoryQuotaEngine, QuotaLimit


def run_cross_tenant_probes(
    *,
    n: int,
    secret: str,
    store: TenantStore,
    metrics_sink: Callable[[str], None] | None = None,
) -> dict:
    """Attempt JWT tenant_id manipulation / wrong-tenant reads. Count leaks vs blocks."""
    # Seed two tenants
    store.set_config("tenant-A")
    store.insert(Record(id="doc-A1", tenant_id="tenant-A", kind="doc", payload={"v": 1}))
    store.set_config("tenant-B")
    store.insert(Record(id="doc-B1", tenant_id="tenant-B", kind="doc", payload={"v": 1}))

    blocked = 0
    leaked = 0
    for i in range(n):
        # Attacker authenticates as A but asks for B's document
        token = issue_token(sub=f"user-A-{i%10}", tenant_id="tenant-A", secret=secret)
        t0 = time.perf_counter()
        try:
            ctx = authenticate(f"Bearer {token}", secret=secret)
            # middleware check against resource tenant
            try:
                enforce_tenant_match(ctx, "tenant-B")
                # If somehow passed, try RLS read
                store.set_config(ctx.claims.tenant_id)
                got = store.get("doc-B1")
                if got is not None:
                    leaked += 1
                else:
                    blocked += 1
            except CrossTenantDenied:
                blocked += 1
        except AuthError:
            blocked += 1
        if metrics_sink:
            metrics_sink("probe")
        _ = (time.perf_counter() - t0) * 1000
    return {
        "attempts": n,
        "blocked": blocked,
        "leaked": leaked,
        "zero_unauthorized": leaked == 0,
    }


def run_quota_abuse(engine: InMemoryQuotaEngine, tenant_id: str, burst: int) -> dict:
    engine.set_limits(
        tenant_id,
        api=QuotaLimit(hard=50, soft=40),
        storage=QuotaLimit(hard=1000, soft=800),
        compute=QuotaLimit(hard=100, soft=80),
    )
    allowed = rejected = 0
    for _ in range(burst):
        d = engine.check_and_consume(tenant_id, "api", 1)
        if d.allowed:
            allowed += 1
        else:
            rejected += 1
    return {"allowed": allowed, "rejected": rejected, "hard_cap": 50}
