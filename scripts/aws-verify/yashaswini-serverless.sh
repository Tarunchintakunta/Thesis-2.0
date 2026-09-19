#!/usr/bin/env bash
# AWS verification for Yashaswini's Serverless Fault Localisation project
# Project: serverless-fault-localisation
# AWS Services: Lambda, CloudWatch, X-Ray, SNS/SQS, SAM

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

PROJECT_NAME="Yashaswini - Serverless Fault Localisation"
PROJECT_DIR="${SCRIPT_DIR}/../../yashaswini-thesis/serverless-fault-localisation"

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
if [[ -f "${PROJECT_DIR}/template.yaml" ]]; then
    log_success "SAM template exists"
else
    log_warning "SAM template not found"
fi

# Verify AWS services
log_info "Checking AWS Lambda access..."
verify_service_access "lambda"

log_info "Checking AWS CloudFormation access..."
verify_service_access "cloudformation"

# Check for simulation mode
if grep -q "sim" "${PROJECT_DIR}/Makefile"; then
    log_success "Project supports simulation mode (no AWS required)"
    
    log_info "Testing simulation mode..."
    if (cd "$PROJECT_DIR" && make sim > /dev/null 2>&1); then
        log_success "Simulation test passed"
    else
        log_warning "Simulation test had issues"
    fi
else
    log_warning "Simulation mode not found in Makefile"
fi

# Check for deployed stack (if live mode)
if [[ "$DRY_RUN" == "0" ]] && check_aws_credentials; then
    log_info "Checking for deployed SAM stack..."
    
    # Check common stack names
    if [[ -f "${PROJECT_DIR}/Makefile" ]]; then
        stack_name=$(grep "STACK ?=" "${PROJECT_DIR}/Makefile" | cut -d= -f2 | tr -d ' ' || echo "faultlab")
        verify_sam_stack "$stack_name"
    fi
fi

print_verification_summary

exit 0
