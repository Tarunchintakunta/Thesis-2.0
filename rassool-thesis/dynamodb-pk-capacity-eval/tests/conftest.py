"""Shared fixtures: in-memory AWS (moto) with the three key designs."""
import boto3
import pytest
from moto import mock_aws

from workloads.generator import keys
from workloads.seed.seed import seed_table

REGION = "eu-west-1"
SMALL = 2000      # orders in the test tables
ZIPF_S = 1.2


def create_table(client, design: str, name: str) -> None:
    schema = keys.KEY_SCHEMA[design]
    ks = [{"AttributeName": schema["hash"], "KeyType": "HASH"}]
    ad = [{"AttributeName": schema["hash"], "AttributeType": "S"}]
    if schema["range"]:
        ks.append({"AttributeName": schema["range"], "KeyType": "RANGE"})
        ad.append({"AttributeName": schema["range"], "AttributeType": "S"})
    client.create_table(TableName=name, KeySchema=ks, AttributeDefinitions=ad, BillingMode="PAY_PER_REQUEST")


@pytest.fixture
def aws(monkeypatch):
    for k, v in {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing",
                 "AWS_SESSION_TOKEN": "testing", "AWS_DEFAULT_REGION": REGION}.items():
        monkeypatch.setenv(k, v)
    with mock_aws():
        yield boto3.client("dynamodb", region_name=REGION)


@pytest.fixture
def tables(aws):
    """One seeded table per key design (on-demand, small)."""
    names = {}
    for d in keys.DESIGNS:
        name = f"test-{d.lower()}"
        create_table(aws, d, name)
        seed_table(name, d, SMALL, kb=1, shards=10, threads=4, client=aws)
        names[d] = name
    return names
