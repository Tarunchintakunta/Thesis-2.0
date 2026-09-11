"""Mutation ground truth from the table stream (moto's DynamoDB Streams)."""
import boto3

from driver.streams import read_stream
from lambda_fn import handler
from tests.conftest import REGION, TABLE
from tests.test_paths import deliver


def stream(ddb):
    arn = ddb.describe_table(TableName=TABLE)["Table"]["LatestStreamArn"]
    return read_stream(boto3.client("dynamodbstreams", region_name=REGION), arn)


def business(events, rid):
    return [e for e in events if e["kind"] == "business" and e["request_id"] == rid]


def test_every_plain_put_shows_up_as_a_state_change(ddb):
    deliver("P1", 3, rid="a")
    ev = business(stream(ddb), "a")
    assert [e["event"] for e in ev] == ["INSERT", "MODIFY", "MODIFY"]
    assert [e["delivery"] for e in ev] == [1, 2, 3]
    assert [e["old_delivery"] for e in ev] == [None, 1, 2]  # item version before / after


def test_guarded_paths_leave_one_business_write(ddb):
    deliver("P2", 5, rid="b")
    deliver("P3", 5, rid="c")
    events = stream(ddb)
    assert len(business(events, "b")) == 1 and len(business(events, "c")) == 1
    key = [e for e in events if e["kind"] == "idem_key" and e["request_id"] == "c"]
    assert [(e["event"], e["status"]) for e in key] == [("INSERT", "IN_PROGRESS"), ("MODIFY", "COMPLETED")]


def test_warmup_calls_do_not_touch_the_table(ddb):
    handler.lambda_handler({"warmup": True})
    assert stream(ddb) == []
