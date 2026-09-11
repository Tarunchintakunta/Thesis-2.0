import json
import random

import pytest

from logad.collect.fake_dynamo import FakeTable
from logad.collect.runtime import VirtualClock, _Capture, load_handler
from tests.conftest import GET_ONE, HEALTH, POST


class Ctx:
    memory_limit_in_mb = 256
    aws_request_id = "req-1"


@pytest.fixture
def handler():
    mod = load_handler()
    cap = _Capture()
    mod.LOG.handlers = [cap]
    mod.LOG.propagate = False
    mod.clock = VirtualClock(0.0)
    mod.capture = cap
    return mod


@pytest.fixture
def table(handler, db_cfg, fault_cfg):
    return FakeTable(handler.clock, random.Random(1), db_cfg, fault_cfg)


def last_record(handler):
    level, message = handler.capture.records[-1]
    return level, json.loads(message)


def test_post_creates_an_order_and_logs_one_json_line(handler, table):
    resp = handler.lambda_handler(POST, Ctx(), table=table)
    assert resp["statusCode"] == 201
    assert len(handler.capture.records) == 1
    level, rec = last_record(handler)
    assert level == "INFO"
    assert set(rec) == {"route", "status", "latency_ms", "cold_start", "error_type", "memory_mb", "downstream_ms"}
    assert rec["route"] == "POST /orders"
    assert rec["error_type"] is None
    assert rec["latency_ms"] > 0  # virtual clock moved by the fake DynamoDB latency


def test_cold_start_flag_only_on_first_call(handler, table):
    handler._COLD_START = True
    handler.lambda_handler(HEALTH, Ctx(), table=table)
    handler.lambda_handler(HEALTH, Ctx(), table=table)
    assert [json.loads(m)["cold_start"] for _, m in handler.capture.records] == [True, False]


def test_get_missing_order_is_404(handler, table):
    assert handler.lambda_handler(GET_ONE, Ctx(), table=table)["statusCode"] == 404
    handler.lambda_handler(POST, Ctx(), table=table)
    assert handler.lambda_handler(GET_ONE, Ctx(), table=table)["statusCode"] == 200


def test_health_does_not_touch_the_table(handler, table):
    handler.lambda_handler(HEALTH, Ctx(), table=table)
    assert table.calls == 0


def test_permission_denied_is_a_logged_500(handler, table):
    table.fault = "permission_denied"
    assert handler.lambda_handler(POST, Ctx(), table=table)["statusCode"] == 500
    level, rec = last_record(handler)
    assert level == "ERROR"
    assert rec["error_type"] == "AccessDeniedException"
    assert "is not authorized to perform: dynamodb:PutItem" in rec["error"]
    # reads still work - only PutItem was removed from the role
    assert handler.lambda_handler(GET_ONE, Ctx(), table=table)["statusCode"] == 404


def test_config_error_breaks_every_table_call(handler, table):
    table.fault = "config_error"
    for event in (POST, GET_ONE):
        assert handler.lambda_handler(event, Ctx(), table=table)["statusCode"] == 500
        assert last_record(handler)[1]["error_type"] == "ResourceNotFoundException"


def test_read_timeout_is_a_504(handler, table, fault_cfg):
    fault_cfg["dependency_timeout"].update(p_hang=0.0, p_timeout=1.0)
    table.fault = "dependency_timeout"
    assert handler.lambda_handler(POST, Ctx(), table=table)["statusCode"] == 504
    rec = last_record(handler)[1]
    assert rec["error_type"] == "DownstreamTimeout"
    assert rec["downstream_ms"] == pytest.approx(2000.0)
