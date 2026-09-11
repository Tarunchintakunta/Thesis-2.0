"""In-memory stand-in for a boto3 DynamoDB ``Table`` used by the emulator.

It raises the *same botocore exceptions* boto3 raises (so the handler's error
handling and the error text in the logs are the real thing) and it moves the
virtual clock forward by a modelled latency on every call.

Fault behaviour (Xie et al., 2025 categories):

* permission_denied   - AccessDeniedException for the removed actions (PutItem)
* config_error        - ResourceNotFoundException (TABLE_NAME points nowhere)
* dependency_timeout  - latency x factor, some calls hit the client read
                        timeout, a few hang past the function timeout
* resource_exhaustion - handled by the runtime (memory), here only slower (GC)
"""
from __future__ import annotations

import math
import random

from botocore.exceptions import ClientError, ReadTimeoutError


class InvocationTimeout(BaseException):
    """The call outlived the function timeout; the runtime kills the invocation."""


class FakeTable:
    def __init__(self, clock, rng: random.Random, db_cfg: dict, fault_cfg: dict,
                 name: str = "orders", account: str = "123456789012", region: str = "eu-west-1",
                 role: str = "orders-api-role", function: str = "orders-api") -> None:
        self.clock = clock
        self.rng = rng
        self.db = db_cfg
        self.fault_cfg = fault_cfg
        self.name = name
        self.account = account
        self.region = region
        self.role = role
        self.function = function
        self.items: dict[str, dict] = {}
        self.fault: str | None = None
        self.deadline: float | None = None  # set by the runtime per invocation
        self.slowdown = 1.0  # set by the runtime (GC pressure)
        self.calls = 0

    # -- helpers ------------------------------------------------------------
    def _latency_s(self) -> float:
        ms = self.rng.lognormvariate(math.log(self.db["latency_median_ms"]), self.db["latency_sigma"])
        if self.fault == "dependency_timeout":
            ms *= self.fault_cfg["dependency_timeout"]["latency_factor"]
        return ms * self.slowdown / 1000.0

    def _wait(self, seconds: float) -> None:
        if self.deadline is not None and self.clock.now + seconds > self.deadline:
            self.clock.now = self.deadline
            raise InvocationTimeout()
        self.clock.advance(seconds)

    def _call(self, op: str, action):
        self.calls += 1
        fault = self.fault
        if fault == "config_error":
            self._wait(self._latency_s())
            raise ClientError({"Error": {"Code": "ResourceNotFoundException",
                                         "Message": "Requested resource not found"}}, op)
        if fault == "permission_denied" and op in self.fault_cfg["permission_denied"]["ops"]:
            self._wait(self._latency_s())
            arn_role = f"arn:aws:sts::{self.account}:assumed-role/{self.role}/{self.function}"
            arn_table = f"arn:aws:dynamodb:{self.region}:{self.account}:table/{self.name}"
            raise ClientError({"Error": {"Code": "AccessDeniedException", "Message": (
                f"User: {arn_role} is not authorized to perform: dynamodb:{op} on resource: "
                f"{arn_table} because no identity-based policy allows the dynamodb:{op} action")}}, op)
        if fault == "dependency_timeout":
            dt = self.fault_cfg["dependency_timeout"]
            roll = self.rng.random()
            if roll < dt["p_hang"]:
                self._wait(dt["hang_s"])  # usually raises InvocationTimeout
            elif roll < dt["p_hang"] + dt["p_timeout"]:
                self._wait(self.db["read_timeout_s"])
                raise ReadTimeoutError(endpoint_url=f"https://dynamodb.{self.region}.amazonaws.com/")
        # background noise that is NOT one of the injected faults: an occasional
        # throttled request, like a real table sometimes returns (0 = off)
        p_throttle = float(self.db.get("p_throttle", 0.0))
        if p_throttle and self.rng.random() < p_throttle:
            self._wait(self._latency_s())
            raise ClientError({"Error": {"Code": "ProvisionedThroughputExceededException", "Message": (
                "The level of configured provisioned throughput for the table was exceeded. "
                "Consider increasing your provisioning level with the UpdateTable API.")}}, op)
        self._wait(self._latency_s())
        return action()

    # -- the Table API the handler uses ------------------------------------------
    def put_item(self, Item: dict, **_kw) -> dict:
        def action():
            self.items[Item["order_id"]] = dict(Item)
            return {}
        return self._call("PutItem", action)

    def get_item(self, Key: dict, **_kw) -> dict:
        def action():
            item = self.items.get(Key["order_id"])
            return {"Item": dict(item)} if item else {}
        return self._call("GetItem", action)

    def scan(self, Limit: int = 20, **_kw) -> dict:
        def action():
            return {"Items": [dict(v) for _, v in zip(range(Limit), self.items.values())]}
        return self._call("Scan", action)
