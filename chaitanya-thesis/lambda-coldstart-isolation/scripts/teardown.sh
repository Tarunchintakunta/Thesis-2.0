#!/usr/bin/env bash
# Remove the study stack when the live campaign is finished (stops any cost).
# CloudWatch log groups are part of the stack and go with it - run
# scripts/collect_logs.py BEFORE this.
set -euo pipefail
STACK=${STACK:-coldstart-study}
REGION=${REGION:-eu-west-1}
aws events disable-rule --name "$STACK-warmer" --region "$REGION" || true
sam delete --stack-name "$STACK" --region "$REGION" --no-prompts
