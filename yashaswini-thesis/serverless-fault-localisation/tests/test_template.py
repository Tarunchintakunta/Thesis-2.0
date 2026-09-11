"""template.yaml agrees with configs/ and the span name mapping (cfn-lint runs in CI)."""
import yaml
from cfnlint.decode import cfn_yaml

from detector.spans import service_names

EXP = yaml.safe_load(open("configs/experiment.yaml"))
TPL = cfn_yaml.load("template.yaml")
RES = TPL["Resources"]


def functions():
    return {k: v for k, v in RES.items() if v["Type"] == "AWS::Serverless::Function"}


def test_one_function_per_service_named_like_the_span_mapping():
    names = {str(v["Properties"]["FunctionName"]["Fn::Sub"]).replace("${AWS::StackName}", EXP["stack_name"])
             for v in functions().values()}
    assert names == set(service_names(EXP["stack_name"], EXP["services"]))


def test_tracing_logging_and_runtime_are_parameters_shared_by_all_functions():
    g = TPL["Globals"]["Function"]
    assert g["Tracing"] == {"Ref": "TracingMode"} and g["Runtime"] == "python3.12" and g["Architectures"] == ["arm64"]
    assert g["Environment"]["Variables"]["LOG_LEVEL"] == {"Ref": "LogLevel"}
    assert set(TPL["Parameters"]["TracingMode"]["AllowedValues"]) == {"Active", "PassThrough"}


def test_api_tracing_and_sampling_rule_follow_the_tracing_switch():
    assert RES["Api"]["Type"] == "AWS::Serverless::Api"  # REST: HTTP APIs cannot be traced by X-Ray
    rule = RES["SamplingRule"]
    assert rule["Condition"] == "TracingOn" and rule["Properties"]["SamplingRule"]["FixedRate"] == {"Ref": "SamplingFixedRate"}


def test_fault_switch_parameter_and_on_demand_table():
    assert RES["FaultParameter"]["Properties"]["Value"] == "{}"
    assert RES["OrdersTable"]["Properties"]["BillingMode"] == "PAY_PER_REQUEST"
    assert all(RES[f"{n}Logs"]["Properties"]["RetentionInDays"] == 14
               for n in ("OrdersApi", "Inventory", "Payments", "Notifications"))
