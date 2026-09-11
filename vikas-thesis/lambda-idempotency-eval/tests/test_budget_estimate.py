import yaml

from scripts import budget_estimate

CFG = yaml.safe_load(open("config/experiment.yaml"))


def test_write_units_per_request():
    assert budget_estimate.write_units("P1", 5, "after_commit") == 5
    assert budget_estimate.write_units("P2", 5, "after_commit") == 5  # failed conditions are billed
    assert budget_estimate.write_units("P3", 1, "after_commit") == 3
    assert budget_estimate.write_units("P3", 5, "after_commit") == 7
    assert budget_estimate.write_units("P3", 5, "p3_between") == 11


def test_campaign_counts():
    c = budget_estimate.phase_counts(CFG, "campaign", 1000)
    assert c["requests"] == 9000 and c["invocations"] == 24000
    assert c["timeouts"] == 15000 and c["wru"] == 30000


def test_whole_study_fits_the_invocation_cap_and_daily_budget():
    rows, total = budget_estimate.estimate(CFG, 1000)
    assert sum(r["invocations"] for r in rows) <= CFG["budget"]["max_invocations"]
    assert 0 < total < CFG["budget"]["daily_usd"]
