import random

from retry.backoff import BackoffConfig, delay_ms, should_retry


def test_backoff_grows_without_jitter():
    cfg = BackoffConfig(base_ms=100, max_ms=10_000, multiplier=2.0, jitter="none")
    assert delay_ms(0, cfg) == 100
    assert delay_ms(1, cfg) == 200
    assert delay_ms(2, cfg) == 400
    assert delay_ms(20, cfg) == 10_000


def test_full_jitter_bounded():
    cfg = BackoffConfig(base_ms=100, max_ms=800, multiplier=2.0, jitter="full")
    rng = random.Random(0)
    for attempt in range(5):
        d = delay_ms(attempt, cfg, rng)
        assert 0 <= d <= 800


def test_should_retry():
    assert should_retry(1, 3)
    assert not should_retry(3, 3)
