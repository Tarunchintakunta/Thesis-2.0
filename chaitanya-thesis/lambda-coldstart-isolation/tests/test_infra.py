"""Static checks on the Terraform stack (warming gate, arch, no paid features)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "terraform/main.tf").read_text()
VARS = (ROOT / "terraform/variables.tf").read_text()


def test_eight_function_keys_three_runtimes():
    for key in (
        "python-default", "python-optimised",
        "nodejs-default", "nodejs-optimised",
        "java-default", "java-optimised",
        "warm-target", "warm-control",
    ):
        assert f'key     = "{key}"' in MAIN or f'key = "{key}"' in MAIN
    assert '"python3.12"' in MAIN and '"nodejs20.x"' in MAIN and '"java21"' in MAIN


def test_arm64_everywhere():
    assert 'architectures    = ["arm64"]' in MAIN or 'architectures = ["arm64"]' in MAIN


def test_no_provisioned_concurrency_or_snapstart():
    assert "provisioned_concurrent" not in MAIN.lower()
    assert "snap_start" not in MAIN.lower() and "SnapStart" not in MAIN


def test_warmer_is_low_frequency_eventbridge_and_off_by_default():
    assert 'name                = "${var.name_prefix}-warmer"' in MAIN or \
           'name = "${var.name_prefix}-warmer"' in MAIN
    assert 'state               = "DISABLED"' in MAIN or 'state = "DISABLED"' in MAIN
    assert 'default = "rate(5 minutes)"' in VARS


def test_packages_match_package_all_outputs():
    for path in (
        "../build/python-default.zip",
        "../build/python-optimised.zip",
        "../build/nodejs-default.zip",
        "../build/nodejs-optimised.zip",
        "../build/java-default/function.jar",
        "../build/java-optimised/function.jar",
    ):
        assert path in VARS


def test_every_function_has_a_log_group_with_retention():
    assert "aws_cloudwatch_log_group" in MAIN
    assert "retention_in_days" in MAIN


def test_function_names_follow_the_backend_convention():
    from coldstart.backends import FUNCTIONS
    # deployed keys (no bytecode — that variant is mock/package-size analysis only)
    deployed = {
        "python-default", "python-optimised",
        "nodejs-default", "nodejs-optimised",
        "java-default", "java-optimised",
        "warm-target", "warm-control",
    }
    assert deployed <= set(FUNCTIONS)
    for key in deployed:
        assert f'key     = "{key}"' in MAIN or f'key = "{key}"' in MAIN
