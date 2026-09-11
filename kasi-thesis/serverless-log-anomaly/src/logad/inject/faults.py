"""The four fault categories, aligned to Xie et al. (2025).

Xie et al. mined 546 real serverless faults; permission errors were the most
frequent symptom. The four categories injected here are the ones the proposal
fixes: permission denial, configuration error, dependency timeout and
resource exhaustion.

Emulator mode: the category is set on the LambdaEmulator / FakeTable.
Live mode (LocalStack or own AWS account): ``LIVE_COMMANDS`` lists what
scripts/03_inject_faults.sh runs to switch each category on and off.
"""
from __future__ import annotations

CATEGORIES = ("permission_denied", "config_error", "dependency_timeout", "resource_exhaustion")

DESCRIPTION = {
    "permission_denied": "dynamodb:PutItem removed from the execution role (deny policy)",
    "config_error": "TABLE_NAME environment variable points to a table that does not exist",
    "dependency_timeout": "DynamoDB made slow: long latency, client read timeouts, some calls hang past the function timeout",
    "resource_exhaustion": "function memory lowered to 128 MB, below the working set (OOM kills, GC slow-down)",
}

# $FN = function name, $ROLE = execution role, $TABLE = table name (see 03_inject_faults.sh)
LIVE_COMMANDS = {
    "permission_denied": {
        "on": ("aws iam put-role-policy --role-name $ROLE --policy-name chaos-deny-put "
               "--policy-document '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Deny\","
               "\"Action\":\"dynamodb:PutItem\",\"Resource\":\"*\"}]}'"),
        "off": "aws iam delete-role-policy --role-name $ROLE --policy-name chaos-deny-put",
    },
    "config_error": {
        "on": "aws lambda update-function-configuration --function-name $FN --environment 'Variables={TABLE_NAME=orders-does-not-exist}'",
        "off": "aws lambda update-function-configuration --function-name $FN --environment 'Variables={TABLE_NAME=$TABLE}'",
    },
    "dependency_timeout": {
        "on": "aws lambda update-function-configuration --function-name $FN --environment 'Variables={TABLE_NAME=$TABLE,DOWNSTREAM_DELAY_MS=2500}'",
        "off": "aws lambda update-function-configuration --function-name $FN --environment 'Variables={TABLE_NAME=$TABLE}'",
    },
    "resource_exhaustion": {
        "on": "aws lambda update-function-configuration --function-name $FN --memory-size 128",
        "off": "aws lambda update-function-configuration --function-name $FN --memory-size 256",
    },
}


def check_category(name: str) -> str:
    if name not in CATEGORIES:
        raise ValueError(f"unknown fault category {name!r}; expected one of {CATEGORIES}")
    return name
