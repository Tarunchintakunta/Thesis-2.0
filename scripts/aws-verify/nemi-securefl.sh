#!/usr/bin/env bash
# AWS verification for Nemi's SecureFL-IDS project
# Live lite FL uses EC2+S3+CloudWatch (not Lambda). Destroy-after-round.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

PROJECT_NAME="Nemi - SecureFL-IDS"
PROJECT_DIR="${SCRIPT_DIR}/../../Nemi/securefl-ids"

print_dry_run_banner "$PROJECT_NAME"

if [[ ! -d "$PROJECT_DIR" ]]; then
    log_error "Project directory not found: ${PROJECT_DIR}"
    exit 1
fi

log_info "Project directory: ${PROJECT_DIR}"

if [[ -f "${PROJECT_DIR}/Makefile" ]]; then
    log_success "Makefile exists"
else
    log_error "Makefile not found"
    exit 1
fi

if [[ -f "${PROJECT_DIR}/results/live/cloud_lite_summary.json" ]]; then
    log_success "Live lite summary present"
else
    log_warning "Live lite summary missing"
fi

log_info "Checking leftover securefl-ids EC2 (should be none after destroy)"
LEFTOVER="$(aws ec2 describe-instances --region eu-west-1 \
  --filters Name=tag:project,Values=securefl-ids Name=instance-state-name,Values=pending,running,stopping \
  --query 'Reservations[].Instances[].InstanceId' --output text 2>/dev/null || true)"
if [[ -z "${LEFTOVER// /}" ]]; then
    log_success "No running securefl-ids instances"
else
    log_error "Leftover instances: ${LEFTOVER}"
    exit 1
fi

print_verification_summary
log_info "AWS verification: live lite recorded; stack should be destroyed"
exit 0
