#!/usr/bin/env bash
# Tear the terraform stack down after a campaign and verify resources are gone.
#   scripts/destroy.sh                 (stage from STACK_NAME or dev)
#   scripts/destroy.sh pilot
set -euo pipefail
cd "$(dirname "$0")/.."

ARG=${1:-${STACK_NAME:-dev}}
case "$ARG" in
  sqs-rr-dev|dev|default) STAGE=dev ;;
  sqs-rr-pilot|pilot)     STAGE=pilot ;;
  sqs-rr-exp|exp)         STAGE=exp ;;
  *) STAGE=$ARG ;;
esac
REGION=${AWS_REGION:-eu-west-1}
TF_DIR=terraform

cd "$TF_DIR"
if [[ ! -d .terraform ]]; then
  terraform init -input=false
fi
terraform destroy -auto-approve -input=false \
  -var="stage=$STAGE" \
  -var="region=$REGION"

mkdir -p ../results
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) teardown verified: terraform destroy stage=$STAGE ($REGION)" | tee -a ../results/teardown_log.txt
