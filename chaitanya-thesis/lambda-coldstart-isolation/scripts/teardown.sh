#!/usr/bin/env bash
# Tear down the study stack when the live campaign is finished (stops any cost).
# Collect CloudWatch logs BEFORE this (scripts/collect_logs.py).
set -euo pipefail
cd "$(dirname "$0")/.."
STACK=${STACK:-coldstart-study}
REGION=${REGION:-eu-west-1}
TF_DIR=terraform

aws events disable-rule --name "$STACK-warmer" --region "$REGION" || true

cd "$TF_DIR"
if [[ ! -d .terraform ]]; then
  terraform init -input=false
fi
terraform destroy -auto-approve -input=false \
  -var="name_prefix=$STACK" \
  -var="region=$REGION"
