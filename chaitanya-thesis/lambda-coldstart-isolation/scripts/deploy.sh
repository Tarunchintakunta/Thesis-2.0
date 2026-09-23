#!/usr/bin/env bash
# Deploy the study stack with Terraform (ethics: self-owned target).
# Needs AWS credentials and packages from package_all.sh.
#
#   bash scripts/package_all.sh && bash scripts/deploy.sh
#   STACK=coldstart-study REGION=eu-west-1 bash scripts/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."

STACK=${STACK:-coldstart-study}
REGION=${REGION:-eu-west-1}
TF_DIR=terraform

for f in build/python-default.zip build/python-optimised.zip build/nodejs-default.zip \
         build/nodejs-optimised.zip build/java-default/function.jar build/java-optimised/function.jar; do
  [ -f "$f" ] || { echo "missing $f - run bash scripts/package_all.sh first" >&2; exit 1; }
done

command -v terraform >/dev/null || { echo "terraform not found" >&2; exit 1; }

echo "deploying $STACK to $REGION in account $(aws sts get-caller-identity --query Account --output text)"
cd "$TF_DIR"
terraform init -input=false
terraform apply -auto-approve -input=false \
  -var="name_prefix=$STACK" \
  -var="region=$REGION" \
  -var="memory_mb=1024" \
  -var="warming_schedule=rate(5 minutes)" \
  -var="enable_tracing=false"

cd ..
mkdir -p data
cp build/package_manifest.json data/package_manifest_deployed.json
echo "done - package manifest copied to data/package_manifest_deployed.json"
