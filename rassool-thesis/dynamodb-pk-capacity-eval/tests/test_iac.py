"""Static checks on the Terraform (the CI job also runs terraform fmt + validate)."""
import json
from pathlib import Path

import hcl2
import yaml

from scripts.render_tfvars import render

IAC = Path(__file__).resolve().parents[1] / "iac"


def load(rel):
    with open(IAC / rel) as fh:
        return hcl2.load(fh)


def text(rel):
    return (IAC / rel).read_text()


def test_six_configurations_from_three_designs_and_two_modes():
    locals_ = {k: v for block in load("main.tf")["locals"] for k, v in block.items()}

    def s(v):  # newer python-hcl2 keeps the quotes of string literals
        return v.strip('"') if isinstance(v, str) else v

    assert set(locals_["designs"]) == {"K1", "K2", "K3"}
    assert set(locals_["modes"]) == {"ondemand", "provisioned"}
    assert s(locals_["modes"]["ondemand"]) == "PAY_PER_REQUEST" and s(locals_["modes"]["provisioned"]) == "PROVISIONED"
    assert s(locals_["designs"]["K2"]["range_key"]) == "orderTs"
    assert "setproduct" in text("main.tf") and "for_each = local.configurations" in text("main.tf")


def test_every_resource_is_tagged_through_default_tags():
    t = text("main.tf")
    assert 'project = "dynamodb-pk-capacity"' in t
    assert 'managed_by = "terraform"' in t
    assert "student" not in t  # no student name/ID in Terraform tags
    assert "default_tags" in t


def test_autoscaling_only_for_provisioned_tables():
    t = text("tables/main.tf")
    assert t.count("count              = local.provisioned ? 1 : 0") == 4
    assert "DynamoDBReadCapacityUtilization" in t and "DynamoDBWriteCapacityUtilization" in t
    assert 'var.billing_mode == "PROVISIONED"' in t


def test_driver_permissions_are_least_privilege():
    t = text("iam/main.tf")
    for action in ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:BatchGetItem", "dynamodb:BatchWriteItem",
                   "dynamodb:DescribeTable", "s3:PutObject", "logs:PutLogEvents"]:
        assert f'"{action}"' in t
    for forbidden in ['"dynamodb:*"', '"dynamodb:DeleteTable"', '"dynamodb:Scan"', '"s3:*"']:
        assert forbidden not in t


def test_lambda_is_arm64_python312():
    t = text("lambda/main.tf")
    assert 'runtime          = "python3.12"' in t and 'architectures    = ["arm64"]' in t
    assert "workloads.lambda_handler.handler.lambda_handler" in t


def test_teardown_is_possible():
    t = text("main.tf")
    assert "force_destroy = true" in t
    assert "deletion_protection_enabled" not in text("tables/main.tf")


def test_tfvars_match_the_capacity_plan():
    cfg = yaml.safe_load(open(IAC.parent / "config/experiment.yaml"))
    assert json.loads((IAC / "terraform.tfvars.json").read_text()) == render(cfg)


def test_throttle_alarm_and_budget_exist():
    t = text("monitoring/main.tf")
    assert "throttle-storm" in t and "aws_budgets_budget" in t and "ReadThrottleEvents" in t
