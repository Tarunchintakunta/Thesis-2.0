"""terraform/ agrees with configs/ and the span name mapping."""
from pathlib import Path

import yaml

EXP = yaml.safe_load(open("configs/experiment.yaml"))
MAIN = Path("terraform/main.tf").read_text()
VARS = Path("terraform/variables.tf").read_text()

from detector.spans import service_names


def test_one_function_per_service_named_like_the_span_mapping():
    expected = set(service_names(EXP["stack_name"], EXP["services"]))
    for name in expected:
        short = name.removeprefix(f"{EXP['stack_name']}-")
        assert f'function_name    = "${{var.name_prefix}}-{short}"' in MAIN or \
               f'function_name = "${{var.name_prefix}}-{short}"' in MAIN
    assert 'default     = "faultlab"' in VARS or 'default = "faultlab"' in VARS


def test_tracing_logging_and_runtime_are_shared():
    assert "python3.12" in MAIN
    assert 'architectures    = ["arm64"]' in MAIN or 'architectures = ["arm64"]' in MAIN
    assert "tracing_mode" in VARS
    assert "Active" in VARS and "PassThrough" in VARS


def test_api_and_sampling_exist():
    assert "aws_api_gateway_rest_api" in MAIN or "aws_apigateway" in MAIN
    assert "aws_xray_sampling_rule" in MAIN or "sampling" in MAIN.lower()


def test_fault_switch_parameter_and_on_demand_table():
    assert "aws_ssm_parameter" in MAIN and "fault" in MAIN
    assert 'billing_mode' in MAIN and "PAY_PER_REQUEST" in MAIN
    assert "retention_in_days" in MAIN
