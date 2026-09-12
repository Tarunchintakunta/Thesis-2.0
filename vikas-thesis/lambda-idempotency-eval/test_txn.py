import boto3
from moto import mock_aws

@mock_aws
def test_transact():
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="test_table",
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )

    # First tx
    dynamodb.transact_write_items(
        TransactItems=[
            {
                "Put": {
                    "TableName": "test_table",
                    "Item": {"pk": {"S": "IDEMP#123"}, "status": {"S": "COMPLETED"}},
                    "ConditionExpression": "attribute_not_exists(pk)",
                    "ReturnValuesOnConditionCheckFailure": "ALL_OLD"
                }
            },
            {
                "Put": {
                    "TableName": "test_table",
                    "Item": {"pk": {"S": "REQ#123"}}
                }
            }
        ]
    )

    # Second tx (should fail)
    import botocore.exceptions
    try:
        dynamodb.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": "test_table",
                        "Item": {"pk": {"S": "IDEMP#123"}, "status": {"S": "NEW_COMPLETED"}},
                        "ConditionExpression": "attribute_not_exists(pk)",
                        "ReturnValuesOnConditionCheckFailure": "ALL_OLD"
                    }
                },
                {
                    "Put": {
                        "TableName": "test_table",
                        "Item": {"pk": {"S": "REQ#123"}}
                    }
                }
            ]
        )
    except botocore.exceptions.ClientError as e:
        print(e.response)

test_transact()