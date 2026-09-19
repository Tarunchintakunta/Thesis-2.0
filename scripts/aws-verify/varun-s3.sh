#!/usr/bin/env bash
# AWS verification for Varun's S3 Predictive Optimization project
# Project: s3-predictive-optimization
# Student: Varun Gampa (23398639)
# AWS Services: S3, CloudWatch (for cost metrics)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

PROJECT_NAME="Varun - S3 Predictive Optimization"
PROJECT_DIR="${SCRIPT_DIR}/../../Varun/s3-predictive-optimization"

print_dry_run_banner "$PROJECT_NAME"

# Check if project directory exists
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

# Verify configuration files
if [[ -f "${PROJECT_DIR}/configs/pilot.yaml" ]]; then
    log_success "Configuration files present"
else
    log_warning "Configuration files may be missing"
fi

# Verify AWS services
log_info "Checking AWS S3 access..."
verify_service_access "s3"

# Check for S3 buckets (if live mode)
if [[ "$DRY_RUN" == "0" ]] && check_aws_credentials; then
    log_info "Checking for project-specific S3 buckets..."
    bucket_count=$(aws s3 ls | grep -c "varun\|s3-opt" || echo "0")
    if [[ "$bucket_count" -gt 0 ]]; then
        log_info "Found ${bucket_count} potential project bucket(s)"
    else
        log_skip "No project-specific buckets found (may not be deployed)"
    fi
fi

# Verify the project supports dry-run mode
if grep -q "DRY_RUN" "${PROJECT_DIR}/Makefile"; then
    log_success "Project supports DRY_RUN mode"
else
    log_warning "DRY_RUN mode may not be implemented"
fi

# Test dry-run mode
log_info "Testing dry-run mode..."
if (cd "$PROJECT_DIR" && make pilot > /dev/null 2>&1); then
    log_success "Dry-run pilot test passed"
else
    log_warning "Dry-run pilot test had issues (check Makefile targets)"
fi

print_verification_summary

exit 0
