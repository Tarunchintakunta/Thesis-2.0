#!/usr/bin/env bash
# Deploy the study stack into the student's OWN AWS account (ethics: self-owned target).
# Needs AWS credentials in the environment, the SAM CLI and build/ from package_all.sh.
#
#   bash scripts/package_all.sh && bash scripts/deploy.sh
#   STACK=coldstart-study REGION=eu-west-1 bash scripts/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."

STACK=${STACK:-coldstart-study}
REGION=${REGION:-eu-west-1}

for f in build/python-default.zip build/python-optimised.zip build/nodejs-default.zip \
         build/nodejs-optimised.zip build/java-default/function.jar build/java-optimised/function.jar; do
  [ -f "$f" ] || { echo "missing $f - run bash scripts/package_all.sh first" >&2; exit 1; }
done

echo "deploying $STACK to $REGION in account $(aws sts get-caller-identity --query Account --output text)"
sam deploy \
  --template-file infra/template.yaml \
  --stack-name "$STACK" \
  --region "$REGION" \
  --resolve-s3 \
  --capabilities CAPABILITY_IAM \
  --no-fail-on-empty-changeset \
  --parameter-overrides MemorySize=1024 "WarmingSchedule=rate(5 minutes)" EnableTracing=false

# keep the exact package sizes and hashes that went to AWS with the data
mkdir -p data
cp build/package_manifest.json data/package_manifest_deployed.json
echo "done - package manifest copied to data/package_manifest_deployed.json"
