from metrics.collect import RunMetrics, percentile


def test_percentile():
    vals = [1, 2, 3, 4, 5]
    assert percentile(vals, 50) == 3
    assert percentile([], 50) == 0.0


def test_rates():
    m = RunMetrics(unique_events=100, delivered_unique=80, duplicate_attempts=10, duplicates_suppressed=9)
    assert abs(m.delivery_success_rate() - 0.8) < 1e-9
    assert abs(m.duplicate_suppression_ratio() - 0.9) < 1e-9
