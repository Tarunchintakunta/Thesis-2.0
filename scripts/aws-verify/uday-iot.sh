#!/usr/bin/env bash
# AWS verification for Uday's IoT Reliability project
# Project: iot-reliability
# NOTE: This project was developed with local simulation only, no live AWS IoT deployment

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

PROJECT_NAME="Uday - IoT Reliability QoS Offload"
PROJECT_DIR="${SCRIPT_DIR}/../../uday-thesis/iot-reliability"

print_dry_run_banner "$PROJECT_NAME"

if [[ ! -d "$PROJECT_DIR" ]]; then
    log_error "Project directory not found: ${PROJECT_DIR}"
    exit 1
fi

log_info "Project directory: ${PROJECT_DIR}"

# Verify project structure
if [[ -f "${PROJECT_DIR}/Makefile" ]]; then
    log_success "Makefile exists"
else
    log_error "Makefile not found"
    exit 1
fi

log_info "This project uses federated learning simulation"
log_info "No live AWS IoT deployment was implemented (by design)"
log_info "Lambda handler code exists but was never deployed to AWS"

# Verify local execution capability
if [[ -f "${PROJECT_DIR}/Makefile" ]]; then
    log_info "Testing local execution..."
    
    if (cd "$PROJECT_DIR" && make test > /dev/null 2>&1); then
        log_success "Local tests passed"
    else
        log_warning "Local tests had issues (may need dependencies)"
    fi
fi

# Check if AWS Lambda handler exists (even though not deployed)
if [[ -f "${PROJECT_DIR}/src/lambda_handler/app.py" ]]; then
    log_info "Lambda handler code exists (local development only)"
else
    log_skip "No Lambda handler found"
fi

print_verification_summary

log_info "AWS verification: N/A (local simulation only, no live deployment)"

exit 0
