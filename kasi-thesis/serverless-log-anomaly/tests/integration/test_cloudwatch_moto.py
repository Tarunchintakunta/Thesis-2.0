import time

import boto3
import pytest
from moto import mock_aws

from logad.collect.cloudwatch import fetch_events, write_log


@pytest.fixture
def logs(monkeypatch):
    for var, value in (("AWS_ACCESS_KEY_ID", "testing"), ("AWS_SECRET_ACCESS_KEY", "testing"),
                       ("AWS_DEFAULT_REGION", "eu-west-1")):
        monkeypatch.setenv(var, value)
    with mock_aws():
        client = boto3.client("logs", region_name="eu-west-1")
        client.create_log_group(logGroupName="/aws/lambda/kasireddy-orders")
        client.create_log_stream(logGroupName="/aws/lambda/kasireddy-orders", logStreamName="s1")
        yield client


def test_fetch_events_sorts_and_splits_lines(logs, tmp_path):
    # CloudWatch (and moto) reject events older than 14 days, so use "now"
    base = int(time.time() * 1000) - 60_000
    logs.put_log_events(logGroupName="/aws/lambda/kasireddy-orders", logStreamName="s1", logEvents=[
        {"timestamp": base + 10, "message": "START RequestId: a Version: $LATEST\n"},
        {"timestamp": base + 20, "message": "RequestId: a Error: Runtime exited with error: signal: killed\nRuntime.ExitError\n"},
        {"timestamp": base + 30, "message": "END RequestId: a\n"},
    ])
    events = fetch_events(logs, "/aws/lambda/kasireddy-orders", base, base + 1000)
    assert [m for _, m in events] == ["START RequestId: a Version: $LATEST",
                                      "RequestId: a Error: Runtime exited with error: signal: killed",
                                      "Runtime.ExitError", "END RequestId: a"]
    path = write_log(events, tmp_path / "live" / "phase_A.log")
    first = path.read_text().splitlines()[0]
    assert first.endswith("\tSTART RequestId: a Version: $LATEST")
    assert first[:4].isdigit() and first[10] == "T"
