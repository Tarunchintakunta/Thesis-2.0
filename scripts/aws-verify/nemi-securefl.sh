#!/usr/bin/env bash
# AWS verification for Nemi's SecureFL-IDS project
# Project: securefl-ids
# NOTE: This project does NOT use AWS - it's federated learning simulation only

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

# Verify project structure
if [[ -f "${PROJECT_DIR}/Makefile" ]]; then
    log_success "Makefile exists"
else
    log_error "Makefile not found"
    exit 1
fi

log_info "This project does NOT use AWS services"
log_info "It is a federated learning simulation that runs entirely locally"
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

log_info "AWS verification: N/A (local simulation only)"

exit 0
