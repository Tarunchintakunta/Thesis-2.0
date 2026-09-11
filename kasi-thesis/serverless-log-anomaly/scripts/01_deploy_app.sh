#!/usr/bin/env bash
# Deploy the Orders API for the live path.
#   TARGET=localstack scripts/01_deploy_app.sh   (default; needs `make localstack-up` first)
#   TARGET=aws        scripts/01_deploy_app.sh   (your own account, sam cli)
# Not needed for the default emulator mode.
set -euo pipefail
cd "$(dirname "$0")/.."
TARGET=${TARGET:-localstack}
STACK=${STACK:-kasireddy-orders}
REGION=${AWS_REGION:-eu-west-1}

if [ "$TARGET" = "aws" ]; then
  command -v sam >/dev/null || { echo "install aws-sam-cli"; exit 1; }
  (cd infra/lambda_app && sam build && sam deploy --stack-name "$STACK" --region "$REGION" \
      --capabilities CAPABILITY_IAM --resolve-s3 --no-confirm-changeset)
  aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
    --query 'Stacks[0].Outputs' --output table
  exit 0
fi

# LocalStack with plain awslocal calls (pip install awscli-local)
command -v awslocal >/dev/null || { echo "install awscli-local (pip install awscli-local)"; exit 1; }
curl -sf http://localhost:4566/_localstack/health >/dev/null || { echo "LocalStack is not running (make localstack-up)"; exit 1; }

awslocal dynamodb create-table --table-name kasireddy-orders --billing-mode PAY_PER_REQUEST \
  --attribute-definitions AttributeName=order_id,AttributeType=S \
  --key-schema AttributeName=order_id,KeyType=HASH >/dev/null || true

awslocal iam create-role --role-name kasireddy-orders-role --assume-role-policy-document \
  '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  >/dev/null || true

TMP=$(mktemp -d)
cp infra/lambda_app/handler.py "$TMP/"
(cd "$TMP" && zip -q function.zip handler.py)
awslocal lambda create-function --function-name kasireddy-orders --runtime python3.11 \
  --handler handler.lambda_handler --zip-file "fileb://$TMP/function.zip" \
  --role arn:aws:iam::000000000000:role/kasireddy-orders-role --memory-size 256 --timeout 3 \
  --environment 'Variables={TABLE_NAME=kasireddy-orders}' >/dev/null || \
awslocal lambda update-function-code --function-name kasireddy-orders --zip-file "fileb://$TMP/function.zip" >/dev/null
awslocal lambda put-function-concurrency --function-name kasireddy-orders --reserved-concurrent-executions 10 >/dev/null

FN_ARN=$(awslocal lambda get-function --function-name kasireddy-orders --query Configuration.FunctionArn --output text)
API_ID=$(awslocal apigatewayv2 create-api --name kasireddy-orders --protocol-type HTTP --target "$FN_ARN" \
  --query ApiId --output text)
echo "API_URL=http://localhost:4566/restapis/$API_ID  (LocalStack HTTP API quick-create)"
echo "ROLE=kasireddy-orders-role FUNCTION=kasireddy-orders TABLE=kasireddy-orders"
