#!/usr/bin/env bash
# Build Lambda zips, then terraform apply into YOUR OWN AWS account.
#   scripts/deploy.sh            -> stage=dev   (sqs-rr-dev)
#   scripts/deploy.sh pilot      -> stage=pilot
#   scripts/deploy.sh exp        -> stage=exp
# Remember scripts/destroy.sh afterwards.
set -euo pipefail
cd "$(dirname "$0")/.."

STAGE=${1:-dev}
case "$STAGE" in
  default|dev) STAGE=dev ;;
  pilot)       STAGE=pilot ;;
  exp)         STAGE=exp ;;
  *) echo "unknown stage $STAGE (use dev|pilot|exp)"; exit 2 ;;
esac
REGION=${AWS_REGION:-eu-west-1}
PY=.venv/bin/python
TF_DIR=terraform

command -v terraform >/dev/null || { echo "terraform not found"; exit 1; }
command -v aws >/dev/null || { echo "aws cli not found"; exit 1; }

echo "== account check"
aws sts get-caller-identity --query Account --output text

echo "== cost estimate"
$PY scripts/estimate_cost.py --config configs/pilot.yaml

echo "== build lambda zips"
bash scripts/build_lambda_zips.sh

echo "== terraform apply (stage=$STAGE in $REGION)"
cd "$TF_DIR"
terraform init -input=false
terraform apply -auto-approve -input=false \
  -var="stage=$STAGE" \
  -var="region=$REGION"
terraform output
echo "export TERRAFORM_DIR=$(pwd)   # for the runner"
echo "runners: python -m src.control.experiment_runner --live --terraform-dir $(pwd) ..."
