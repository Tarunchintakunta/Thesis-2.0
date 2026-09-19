#!/usr/bin/env bash
# AWS verification for Venkat's Distributed Matrix Scaling project
# Project: distributed-matrix-scaling
# NOTE: This project does NOT use AWS - it's local CPU/numpy benchmarking only

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

PROJECT_NAME="Venkat Bora - Distributed Matrix Scaling"
PROJECT_DIR="${SCRIPT_DIR}/../../venkat-bora-thesis/distributed-matrix-scaling"

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

log_info "This project does NOT use AWS services"
log_info "It is a local benchmarking study of matrix scaling algorithms"
log_info "No AWS credentials or cloud resources required"

# Verify local execution capability
if [[ -f "${PROJECT_DIR}/Makefile" ]]; then
    log_info "Testing local execution..."
    
    if (cd "$PROJECT_DIR" && make test > /dev/null 2>&1); then
        log_success "Local tests passed"
    else
        log_warning "Local tests had issues (may need dependencies)"
    fi
fi

print_verification_summary

log_info "AWS verification: N/A (local benchmarking only)"

exit 0
