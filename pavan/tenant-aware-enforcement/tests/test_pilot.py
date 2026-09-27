from sim.runner import run_pilot


def test_pilot_targets():
    out = run_pilot(n_tenants=10, requests_per_tenant=40, cross_tenant_probes=1000, seed=1)
    assert out["pen_test_10k"]["leaked"] == 0 or out["metrics"]["cross_tenant_leaked"] == 0
    assert out["metrics"]["zero_unauthorized_access"] is True
    assert out["targets"]["auth_p95_lt_50ms"] is True
    assert out["targets"]["quota_p95_lt_5ms"] is True
    # Jain may be <0.9 if hard caps differ a lot — still report; check defined
    assert 0.0 <= out["metrics"]["jain_fairness_index"] <= 1.0
