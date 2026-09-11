"""Static checks on the SAM template (warming gate, arch, no paid features)."""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class CfnLoader(yaml.SafeLoader):
    pass


def _tag(loader, suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return {suffix: loader.construct_scalar(node)}
    if isinstance(node, yaml.SequenceNode):
        return {suffix: loader.construct_sequence(node)}
    return {suffix: loader.construct_mapping(node)}


CfnLoader.add_multi_constructor("!", _tag)
TEMPLATE = yaml.load((ROOT / "infra/template.yaml").read_text(), Loader=CfnLoader)
TEXT = (ROOT / "infra/template.yaml").read_text()
FUNCS = {k: v for k, v in TEMPLATE["Resources"].items() if v["Type"] == "AWS::Serverless::Function"}


def test_eight_functions_three_runtimes():
    assert len(FUNCS) == 8
    assert {f["Properties"]["Runtime"] for f in FUNCS.values()} == {"python3.12", "nodejs20.x", "java21"}


def test_arm64_everywhere():
    assert TEMPLATE["Globals"]["Function"]["Architectures"] == ["arm64"]
    assert not any("Architectures" in f["Properties"] for f in FUNCS.values())


def test_no_provisioned_concurrency_or_snapstart():
    assert "ProvisionedConcurrency" not in TEXT
    assert "SnapStart" not in TEXT.replace("no SnapStart", "")


def test_warmer_is_low_frequency_eventbridge_and_off_by_default():
    events = FUNCS["WarmTargetFunction"]["Properties"]["Events"]
    warmer = events["Warmer"]
    assert warmer["Type"] == "Schedule"
    assert warmer["Properties"]["State"] == "DISABLED"
    assert TEMPLATE["Parameters"]["WarmingSchedule"]["Default"] == "rate(5 minutes)"
    assert "Events" not in FUNCS["WarmControlFunction"]["Properties"]
    js = json.loads((ROOT / "scripts/warmer_schedule.json").read_text())
    assert js["ScheduleExpression"] == TEMPLATE["Parameters"]["WarmingSchedule"]["Default"]


def test_warming_pair_is_identical_apart_from_the_rule():
    a = dict(FUNCS["WarmTargetFunction"]["Properties"])
    b = dict(FUNCS["WarmControlFunction"]["Properties"])
    a.pop("Events")
    a.pop("FunctionName")
    b.pop("FunctionName")
    assert a == b


def test_code_uris_match_package_all_outputs():
    uris = {f["Properties"]["CodeUri"] for f in FUNCS.values()}
    expected = {"../build/python-default.zip", "../build/python-optimised.zip", "../build/nodejs-default.zip",
                "../build/nodejs-optimised.zip", "../build/java-default/function.jar",
                "../build/java-optimised/function.jar"}
    assert uris == expected


def test_every_function_has_a_log_group_with_retention():
    groups = [v for v in TEMPLATE["Resources"].values() if v["Type"] == "AWS::Logs::LogGroup"]
    assert len(groups) == 8
    assert all("RetentionInDays" in g["Properties"] for g in groups)


def test_function_names_follow_the_backend_convention():
    from coldstart.backends import FUNCTIONS
    names = {f["Properties"]["FunctionName"]["Sub"].replace("${AWS::StackName}-", "") for f in FUNCS.values()}
    assert names == set(FUNCTIONS)
