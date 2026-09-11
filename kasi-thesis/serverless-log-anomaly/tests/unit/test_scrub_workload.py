import random

import pytest

from logad.collect.scrub import has_identifiers, scrub
from logad.collect.workload import Burst, arrivals, diurnal_rate, make_event, pick_route, regular_bursts

LINE = ("[ERROR]\t2026-06-01T10:00:00.000Z\t8f5a3c1e-1b2c-4d3e-9f00-123456789abc\t"
        '{"error": "User: arn:aws:sts::123456789012:assumed-role/r/f is not authorized", "ip": "10.1.2.3", '
        '"order": "ord-0123456789ab"}')


def test_scrub_removes_every_identifier():
    out = scrub(LINE)
    assert "<RID>" in out and "<ACCT>" in out and "<IP>" in out and "<ORDER>" in out
    assert "123456789012" not in out
    assert not has_identifiers(out)
    assert has_identifiers(LINE)


def test_scrub_keeps_status_codes_and_sizes():
    line = "REPORT RequestId: x\tDuration: 12.34 ms\tMemory Size: 256 MB"
    assert scrub(line) == line


def test_diurnal_rate_has_a_night_low_and_an_afternoon_high():
    base = 1.0
    night = diurnal_rate(4 * 3600, base, 0.7)
    afternoon = diurnal_rate(16 * 3600, base, 0.7)
    assert night == pytest.approx(0.3)
    assert afternoon == pytest.approx(1.7)


def test_arrivals_follow_the_rate():
    rng = random.Random(0)
    times = arrivals(0, 3600, 2.0, 0.0, [], rng)
    assert 6800 < len(times) < 7600
    assert times == sorted(times)


def test_bursts_add_load_only_inside_the_burst():
    rng = random.Random(0)
    burst = Burst(1000, 100, 10)
    times = arrivals(0, 2000, 1.0, 0.0, [burst], rng)
    inside = sum(1000 <= t < 1100 for t in times)
    outside = len(times) - inside
    assert inside > 5 * (outside / 19)  # ~10x the rate of an average 100 s slot


def test_regular_bursts_fit_their_slots():
    rng = random.Random(1)
    bursts = regular_bursts(0, 7200, 1800, 180, 40, rng)
    assert len(bursts) == 4
    assert all(0 <= b.start and b.start + b.length <= 7200 for b in bursts)


def test_route_mix_and_events():
    rng = random.Random(2)
    mix = {"POST /orders": 0.5, "GET /health": 0.5}
    routes = [pick_route(mix, rng) for _ in range(1000)]
    assert 400 < routes.count("POST /orders") < 600
    ids: list[str] = []
    post = make_event("POST /orders", rng, ids)
    assert post["routeKey"] == "POST /orders" and ids and ids[0] in post["body"]
    get = make_event("GET /orders/{id}", rng, ids)
    assert "id" in get["pathParameters"]
