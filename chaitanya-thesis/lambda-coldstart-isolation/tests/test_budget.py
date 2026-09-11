import pytest

from coldstart.budget import BudgetExceeded, BudgetGuard
from coldstart.mock import EPOCH0

DAY = 86400


def test_guard_stops_when_cap_reached(tmp_path):
    g = BudgetGuard(0.01, tmp_path / "s.csv", "mock")
    g.check(EPOCH0, 128)
    g.charge(EPOCH0, "python-default", 3008, 1_000_000)  # ~$0.04, more than the cap
    with pytest.raises(BudgetExceeded):
        g.check(EPOCH0 + 1, 128)


def test_spend_log_is_read_back(tmp_path):
    log = tmp_path / "s.csv"
    BudgetGuard(1.0, log, "mock").charge(EPOCH0, "java-default", 1024, 5000)
    g = BudgetGuard(1.0, log, "mock")
    assert g.spent(EPOCH0) > 0
    assert log.read_text().splitlines()[0].startswith("utc_day,")


def test_new_utc_day_starts_from_zero(tmp_path):
    g = BudgetGuard(0.01, tmp_path / "s.csv", "mock")
    g.charge(EPOCH0, "python-default", 3008, 1_000_000)
    g.check(EPOCH0 + DAY, 128)  # next day, no exception
    assert g.spent(EPOCH0 + DAY) == 0


def test_worst_case_uses_timeout_and_memory(tmp_path):
    g = BudgetGuard(0.0005, tmp_path / "s.csv", "mock", timeout_s=30)
    g.check(EPOCH0, 128)  # 30 s at 128 MB ~ $0.00005
    with pytest.raises(BudgetExceeded):
        g.check(EPOCH0, 3008)  # 30 s at 3008 MB ~ $0.0012
