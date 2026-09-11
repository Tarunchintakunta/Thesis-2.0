import boto3
import pytest
from moto import mock_aws

REGION = "eu-west-1"
TABLE = "idem-test"


def make_table(client, name=TABLE):
    client.create_table(TableName=name, KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                        BillingMode="PAY_PER_REQUEST",
                        StreamSpecification={"StreamEnabled": True, "StreamViewType": "NEW_AND_OLD_IMAGES"})


@pytest.fixture
def ddb(monkeypatch):
    for k, v in {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing", "AWS_SESSION_TOKEN": "testing",
                 "AWS_DEFAULT_REGION": REGION, "INJECT_MODE": "raise", "TABLE_NAME": TABLE}.items():
        monkeypatch.setenv(k, v)
    with mock_aws():
        c = boto3.client("dynamodb", region_name=REGION)
        make_table(c)
        from lambda_fn import handler
        monkeypatch.setattr(handler, "_CLIENT", None)  # a fresh client inside this mock
        monkeypatch.setattr(handler, "_COLD", True)
        yield c
