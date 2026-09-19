#!/usr/bin/env bash
# AWS verification for Chaitanya's Lambda Cold-Start Isolation project
# Project: lambda-coldstart-isolation
# AWS Services: Lambda, EventBridge, CloudWatch, SAM

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

PROJECT_NAME="Chaitanya - Lambda Cold-Start Isolation"
PROJECT_DIR="${SCRIPT_DIR}/../../chaitanya-thesis/lambda-coldstart-isolation"

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

# Check for SAM template
if [[ -f "${PROJECT_DIR}/infra/template.yaml" ]]; then
    log_success "SAM template exists"
else
    log_warning "SAM template not found"
fi

# Verify AWS services
log_info "Checking AWS Lambda access..."
verify_service_access "lambda"

log_info "Checking AWS CloudFormation access..."
verify_service_access "cloudformation"

# Check for deployed SAM stack (if live mode)
if [[ "$DRY_RUN" == "0" ]] && check_aws_credentials; then
    log_info "Checking for deployed SAM stack..."
    
    # Common stack names for this project
    for stack_name in "lambda-coldstart-dev" "lambda-coldstart" "chaitanya-lambda"; do
        if aws cloudformation describe-stacks --stack-name "$stack_name" > /dev/null 2>&1; then
            log_success "Found stack: ${stack_name}"
            break
        fi
    done
fi

# Verify proxy benchmark capability (local mode)
if [[ -d "${PROJECT_DIR}/data/proxy" ]] || grep -q "proxy" "${PROJECT_DIR}/Makefile"; then
    log_success "Project supports local proxy benchmarks (no AWS required)"
else
    log_info "Local proxy benchmarks may not be configured"
fi

print_verification_summary

log_info "NOTE: This project was developed with local validation only"
log_info "See STATUS.md for details on proxy benchmarking approach"

exit 0
