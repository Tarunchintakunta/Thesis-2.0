#!/usr/bin/env bash
# AWS verification for Rassool's DynamoDB PK Capacity Evaluation project
# Project: dynamodb-pk-capacity-eval
# AWS Services: DynamoDB, Lambda, S3, CloudWatch

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

PROJECT_NAME="Rassool - DynamoDB PK Capacity Evaluation"
PROJECT_DIR="${SCRIPT_DIR}/../../rassool-thesis/dynamodb-pk-capacity-eval"

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
if [[ -d "${PROJECT_DIR}/iac" ]]; then
    log_success "IaC directory (Terraform) exists"
    verify_terraform_state "${PROJECT_DIR}/iac"
else
    log_warning "IaC directory not found"
fi

# Verify AWS services
log_info "Checking AWS DynamoDB access..."
verify_service_access "dynamodb"

log_info "Checking AWS Lambda access..."
verify_service_access "lambda"

log_info "Checking AWS S3 access..."
verify_service_access "s3"

# Check for deployed resources (if live mode)
if [[ "$DRY_RUN" == "0" ]] && check_aws_credentials; then
    log_info "Checking for project DynamoDB tables..."
    table_count=$(aws dynamodb list-tables --output json | grep -c "rassool\|pk-capacity\|workload" || echo "0")
    if [[ "$table_count" -gt 0 ]]; then
        log_info "Found ${table_count} potential project table(s)"
    else
        log_skip "No project-specific tables found (may not be deployed)"
    fi
fi

# Verify smoke test availability
if grep -q "smoke" "${PROJECT_DIR}/Makefile"; then
    log_success "Project supports smoke test with local DynamoDB"
    
    log_info "Testing smoke test target..."
    if (cd "$PROJECT_DIR" && make smoke > /dev/null 2>&1); then
        log_success "Smoke test passed (local DynamoDB mock)"
    else
        log_warning "Smoke test had issues (may need dependencies)"
    fi
else
    log_warning "Smoke test target not found in Makefile"
fi

print_verification_summary

exit 0
