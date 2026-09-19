#!/usr/bin/env bash
# AWS verification for Vikas's Lambda Idempotency Evaluation project
# Project: lambda-idempotency-eval
# AWS Services: Lambda, DynamoDB, Kinesis, CloudWatch

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

PROJECT_NAME="Vikas - Lambda Idempotency Evaluation"
PROJECT_DIR="${SCRIPT_DIR}/../../vikas-thesis/lambda-idempotency-eval"

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

# Check for Terraform infrastructure
if [[ -d "${PROJECT_DIR}/infra" ]]; then
    log_success "IaC directory (Terraform) exists"
    verify_terraform_state "${PROJECT_DIR}/infra"
else
    log_warning "IaC directory not found"
fi

# Verify AWS services
log_info "Checking AWS Lambda access..."
verify_service_access "lambda"

log_info "Checking AWS DynamoDB access..."
verify_service_access "dynamodb"

# Check for functional test (moto/local mode)
if grep -q "functional" "${PROJECT_DIR}/Makefile"; then
    log_success "Project supports functional testing with moto (no AWS required)"
    
    log_info "Testing functional mode..."
    if (cd "$PROJECT_DIR" && make functional > /dev/null 2>&1); then
        log_success "Functional test passed (moto simulator)"
    else
        log_warning "Functional test had issues (may need dependencies)"
    fi
else
    log_warning "Functional test target not found"
fi

# Check for deployed infrastructure (if live mode)
if [[ "$DRY_RUN" == "0" ]] && check_aws_credentials; then
    log_info "Checking for deployed Terraform resources..."
    
    if [[ -f "${PROJECT_DIR}/infra/terraform.tfstate" ]]; then
        log_info "Terraform state exists - resources may be deployed"
    else
        log_skip "No Terraform state found (infrastructure not deployed)"
    fi
fi

print_verification_summary

exit 0
