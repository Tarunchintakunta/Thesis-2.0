"""Live fault switching against LocalStack or the researcher's own AWS account.

Each category is turned on/off with the same change an operator would make by
mistake (see ``faults.LIVE_COMMANDS``), done here through boto3 so it can be
scheduled from Python and unit tested against moto:

* permission_denied   - inline Deny policy for dynamodb:PutItem on the execution role
* config_error        - TABLE_NAME points to a table that does not exist
* dependency_timeout  - DOWNSTREAM_DELAY_MS makes every DynamoDB call slow
* resource_exhaustion - memory lowered to 128 MB

Not executed in this repository against a real endpoint (no Docker/LocalStack
while building it) - the calls are tested with moto.
"""
from __future__ import annotations

import json

from logad.inject.faults import check_category

DENY_POLICY = {"Version": "2012-10-17",
               "Statement": [{"Effect": "Deny", "Action": "dynamodb:PutItem", "Resource": "*"}]}


class LiveFaultSwitch:
    def __init__(self, lambda_client, iam_client, function_name: str, role_name: str, table_name: str,
                 normal_memory_mb: int = 256, exhausted_memory_mb: int = 128, delay_ms: int = 2500) -> None:
        self.lam = lambda_client
        self.iam = iam_client
        self.function_name = function_name
        self.role_name = role_name
        self.table_name = table_name
        self.normal_memory_mb = normal_memory_mb
        self.exhausted_memory_mb = exhausted_memory_mb
        self.delay_ms = delay_ms
        self.active: str | None = None

    def _set_env(self, extra: dict | None = None, table: str | None = None) -> None:
        variables = {"TABLE_NAME": table or self.table_name, **(extra or {})}
        self.lam.update_function_configuration(FunctionName=self.function_name,
                                               Environment={"Variables": variables})

    def on(self, category: str) -> None:
        check_category(category)
        if category == "permission_denied":
            self.iam.put_role_policy(RoleName=self.role_name, PolicyName="chaos-deny-put",
                                     PolicyDocument=json.dumps(DENY_POLICY))
        elif category == "config_error":
            self._set_env(table="orders-does-not-exist")
        elif category == "dependency_timeout":
            self._set_env({"DOWNSTREAM_DELAY_MS": str(self.delay_ms)})
        elif category == "resource_exhaustion":
            self.lam.update_function_configuration(FunctionName=self.function_name,
                                                   MemorySize=self.exhausted_memory_mb)
        self.active = category

    def off(self) -> None:
        if self.active == "permission_denied":
            self.iam.delete_role_policy(RoleName=self.role_name, PolicyName="chaos-deny-put")
        elif self.active in ("config_error", "dependency_timeout"):
            self._set_env()
        elif self.active == "resource_exhaustion":
            self.lam.update_function_configuration(FunctionName=self.function_name,
                                                   MemorySize=self.normal_memory_mb)
        self.active = None
