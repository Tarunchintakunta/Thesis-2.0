#!/usr/bin/env bash
# Destroy the mqtt-qos lite/smoke stack completely and scrub local certs.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TF_DIR="${ROOT}/terraform"
CERTS="${ROOT}/.certs"

STAGE="${TF_VAR_stage:-lite}"
DEVICE_COUNT="${TF_VAR_device_count:-5}"
REGION="${AWS_DEFAULT_REGION:-eu-west-1}"

if [[ -f "${CERTS}/stack_meta.json" ]]; then
  META_JSON="$(cat "${CERTS}/stack_meta.json")"
  STAGE="$(printf '%s' "${META_JSON}" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("name_prefix","mqtt-qos-lite").rsplit("-",1)[-1])')"
  REGION="$(printf '%s' "${META_JSON}" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("region","eu-west-1"))')"
  DEVICE_COUNT="$(printf '%s' "${META_JSON}" | python3 -c 'import json,sys; print(len(json.load(sys.stdin).get("thing_names",[])) or 5)')"
fi

cd "${TF_DIR}"

if [[ ! -d .terraform ]]; then
  terraform init -input=false >/dev/null
fi

echo "destroy_stack: stage=${STAGE} device_count=${DEVICE_COUNT} region=${REGION}"
set +e
terraform destroy -auto-approve \
  -var="enable_apply=true" \
  -var="device_count=${DEVICE_COUNT}" \
  -var="stage=${STAGE}" \
  -var="region=${REGION}"
TF_RC=$?
set -e

if [[ -d "${CERTS}" ]]; then
  echo "destroy_stack: removing ${CERTS}"
  rm -rf "${CERTS}"
fi

echo "destroy_stack: done (terraform_rc=${TF_RC})"
exit 0
