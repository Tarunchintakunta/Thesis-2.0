"""Live fault switch against moto's IAM + Lambda (no real account)."""
import io
import json
import zipfile

import boto3
import pytest
from moto import mock_aws

from logad.inject.live import LiveFaultSwitch

REGION = "eu-west-1"
TRUST = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"},
                                                  "Action": "sts:AssumeRole"}]}


@pytest.fixture
def switch(monkeypatch):
    for var, value in (("AWS_ACCESS_KEY_ID", "testing"), ("AWS_SECRET_ACCESS_KEY", "testing"),
                       ("AWS_DEFAULT_REGION", REGION)):
        monkeypatch.setenv(var, value)
    with mock_aws():
        iam = boto3.client("iam", region_name=REGION)
        role = iam.create_role(RoleName="orders-role", AssumeRolePolicyDocument=json.dumps(TRUST))["Role"]
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("handler.py", "def lambda_handler(event, context):\n    return {}\n")
        lam = boto3.client("lambda", region_name=REGION)
        lam.create_function(FunctionName="orders", Runtime="python3.11", Role=role["Arn"],
                            Handler="handler.lambda_handler", Code={"ZipFile": buf.getvalue()}, MemorySize=256,
                            Environment={"Variables": {"TABLE_NAME": "orders-table"}})
        yield LiveFaultSwitch(lam, iam, "orders", "orders-role", "orders-table"), lam, iam


def config(lam):
    return lam.get_function_configuration(FunctionName="orders")


def test_permission_denied_adds_and_removes_a_deny_policy(switch):
    sw, _, iam = switch
    sw.on("permission_denied")
    assert iam.list_role_policies(RoleName="orders-role")["PolicyNames"] == ["chaos-deny-put"]
    sw.off()
    assert iam.list_role_policies(RoleName="orders-role")["PolicyNames"] == []


def test_config_error_and_timeout_change_the_environment(switch):
    sw, lam, _ = switch
    sw.on("config_error")
    assert config(lam)["Environment"]["Variables"]["TABLE_NAME"] == "orders-does-not-exist"
    sw.off()
    assert config(lam)["Environment"]["Variables"] == {"TABLE_NAME": "orders-table"}
    sw.on("dependency_timeout")
    assert config(lam)["Environment"]["Variables"]["DOWNSTREAM_DELAY_MS"] == "2500"
    sw.off()
    assert "DOWNSTREAM_DELAY_MS" not in config(lam)["Environment"]["Variables"]


def test_resource_exhaustion_lowers_memory(switch):
    sw, lam, _ = switch
    sw.on("resource_exhaustion")
    assert config(lam)["MemorySize"] == 128
    sw.off()
    assert config(lam)["MemorySize"] == 256
    assert sw.active is None


def test_unknown_category_is_rejected(switch):
    sw, _, _ = switch
    with pytest.raises(ValueError):
        sw.on("solar_flare")
