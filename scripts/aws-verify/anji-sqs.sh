#!/usr/bin/env bash
# AWS verification for Anji's SQS Reliability Recovery project
# Project: sqs-reliability-recovery
# AWS Services: SQS, Lambda, CloudWatch, CloudFormation/SAM

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

PROJECT_NAME="Anji - SQS Reliability Recovery"
PROJECT_DIR="${SCRIPT_DIR}/../../anji-thesis/sqs-reliability-recovery"

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

# Check for CloudFormation template
if [[ -f "${PROJECT_DIR}/template.yaml" ]]; then
    log_success "CloudFormation/SAM template exists"
else
    log_warning "CloudFormation template not found"
fi

# Verify AWS services
log_info "Checking AWS SQS access..."
verify_service_access "sqs"

log_info "Checking AWS Lambda access..."
verify_service_access "lambda"

# Verify the project supports dry-run mode
if grep -q "DRY_RUN" "${PROJECT_DIR}/Makefile"; then
    log_success "Project supports DRY_RUN mode"
else
    log_warning "DRY_RUN mode may not be implemented"
fi

# Test pilot in dry-run mode
log_info "Testing dry-run pilot..."
if (cd "$PROJECT_DIR" && make pilot > /dev/null 2>&1); then
    log_success "Dry-run pilot passed (local simulator)"
else
    log_warning "Dry-run pilot had issues"
fi

# Check for deployed stack (if live mode)
if [[ "$DRY_RUN" == "0" ]] && check_aws_credentials; then
    log_info "Checking for deployed CloudFormation stack..."
    
    if [[ -f "${PROJECT_DIR}/Makefile" ]]; then
        stack_name=$(grep "STACK ?=" "${PROJECT_DIR}/Makefile" | cut -d= -f2 | tr -d ' ' || echo "sqs-rr-dev")
        verify_sam_stack "$stack_name"
    fi
fi

print_verification_summary

exit 0
