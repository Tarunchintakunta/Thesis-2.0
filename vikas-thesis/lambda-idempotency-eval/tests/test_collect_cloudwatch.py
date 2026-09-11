import json

import boto3
from botocore.stub import Stubber

from scripts import collect_cloudwatch


def fake_run(tmp_path):
    (tmp_path / "run_info.json").write_text(json.dumps({"t_start": 1_790_000_000, "t_end": 1_790_000_600,
                                                        "warmup": {"calls": 2}}))
    rows = [{"status": "timeout", "wcu": 1.0, "rcu": 0.0, "wcu_ccf_rule": 0.0},
            {"status": "timeout", "wcu": 0.0, "rcu": 0.0, "wcu_ccf_rule": 1.0},  # failed condition
            {"status": "ok", "wcu": 0.0, "rcu": 0.0, "wcu_ccf_rule": 1.0}]
    (tmp_path / "deliveries.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return tmp_path


def test_cloudwatch_totals_are_set_against_the_driver(tmp_path):
    cw = boto3.client("cloudwatch", region_name="eu-west-1", aws_access_key_id="x", aws_secret_access_key="x")
    with Stubber(cw) as stub:
        for value in (3.0, 0.0, 5.0, 2.0):  # write units, read units, invocations, errors
            stub.add_response("get_metric_statistics", {"Datapoints": [{"Sum": value}]})
        res = collect_cloudwatch.cross_check(cw, fake_run(tmp_path), "t", "f")
    c = res["compare"]
    assert c["wcu_cloudwatch_minus_reported"] == 2.0  # CloudWatch saw the failed conditions ...
    assert c["wcu_cloudwatch_minus_reported_plus_rule"] == 0.0  # ... exactly as the rule says
    assert c["invocations_minus_driver"] == 0.0 and c["errors_minus_timeouts_and_errors"] == 0.0
