from metrics.fairness import jain_index
from quota.redis_quota import InMemoryQuotaEngine, QuotaLimit


def test_jain_perfect():
    assert abs(jain_index([10, 10, 10]) - 1.0) < 1e-9


def test_hard_limit():
    e = InMemoryQuotaEngine()
    e.set_limits("t", api=QuotaLimit(hard=5, soft=4), storage=QuotaLimit(100, 80), compute=QuotaLimit(100, 80))
    ok = sum(1 for _ in range(10) if e.check_and_consume("t", "api").allowed)
    assert ok == 5


def test_quota_latency_budget():
    e = InMemoryQuotaEngine()
    d = e.check_and_consume("t", "api")
    assert d.latency_ms < 5.0
