from security.pen_tests import run_cross_tenant_probes
from db.store import TenantStore


def test_10k_zero_leak_smoke():
    # smaller n in unit test; full 10k in pilot
    r = run_cross_tenant_probes(n=500, secret="s", store=TenantStore(rls_enabled=True))
    assert r["leaked"] == 0
    assert r["blocked"] == 500
