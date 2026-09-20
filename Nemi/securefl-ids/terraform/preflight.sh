#!/usr/bin/env bash
# Local-only Terraform validate for SecureFL-IDS. Never apply from this script.
set -euo pipefail
cd "$(dirname "$0")"
echo "Nemi cloud-FL preflight (validate only; apply forbidden here)"
if [[ "${ALLOW_TF_APPLY:-}" == "1" ]]; then
  echo "Refusing: this script never applies. Unset ALLOW_TF_APPLY." >&2
  exit 2
fi
terraform fmt -check
terraform init -backend=false -input=false >/tmp/nemi-tf-init.log
terraform validate
echo "OK: terraform validate passed. Do not apply while shared-account concurrency is hot."
