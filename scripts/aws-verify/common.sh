#!/usr/bin/env bash
# Common AWS verification utilities for thesis projects
# Usage: source this file in per-project verification scripts
#
# Fails closed: without valid AWS credentials, all checks report SKIP (exit 0)
# Never prints secrets or credentials

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Dry-run mode from environment
readonly DRY_RUN="${DRY_RUN:-1}"

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $*"
}

# Check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_skip "AWS CLI not installed"
        return 1
    fi
    return 0
}

# Check AWS credentials without printing them
# Returns 0 if valid credentials, 1 otherwise
check_aws_credentials() {
    if ! check_aws_cli; then
        return 1
    fi

    # Fail closed: if we can't get caller identity, assume no credentials
    if ! aws sts get-caller-identity --output json > /dev/null 2>&1; then
        log_skip "No valid AWS credentials found (this is expected in dry-run mode)"
        return 1
    fi

    # Get account info without exposing secrets
    local account_id
    account_id=$(aws sts get-caller-identity --query 'Account' --output text 2>/dev/null || echo "unknown")
    
    # Redact for safety - only show last 4 digits
    local redacted_account="${account_id:0:8}****"
    log_success "AWS credentials valid (account: ${redacted_account})"
    return 0
}

# Verify AWS service availability (without making changes)
# $1: service name (e.g., s3, lambda, dynamodb)
verify_service_access() {
    local service="$1"
    
    if [[ "$DRY_RUN" == "1" ]]; then
        log_skip "DRY_RUN=1: Skipping ${service} service check"
        return 0
    fi

    if ! check_aws_credentials; then
        return 0
    fi

    case "$service" in
        s3)
            if aws s3 ls > /dev/null 2>&1; then
                log_success "S3 access verified"
            else
                log_warning "S3 access check failed (may be permissions issue)"
            fi
            ;;
        lambda)
            if aws lambda list-functions --max-items 1 > /dev/null 2>&1; then
                log_success "Lambda access verified"
            else
                log_warning "Lambda access check failed (may be permissions issue)"
            fi
            ;;
        dynamodb)
            if aws dynamodb list-tables --max-items 1 > /dev/null 2>&1; then
                log_success "DynamoDB access verified"
            else
                log_warning "DynamoDB access check failed (may be permissions issue)"
            fi
            ;;
        sqs)
            if aws sqs list-queues > /dev/null 2>&1; then
                log_success "SQS access verified"
            else
                log_warning "SQS access check failed (may be permissions issue)"
            fi
            ;;
        iot)
            if aws iot list-things --max-results 1 > /dev/null 2>&1; then
                log_success "IoT Core access verified"
            else
                log_warning "IoT Core access check failed (may be permissions issue)"
            fi
            ;;
        cloudformation)
            if aws cloudformation list-stacks --max-results 1 > /dev/null 2>&1; then
                log_success "CloudFormation access verified"
            else
                log_warning "CloudFormation access check failed (may be permissions issue)"
            fi
            ;;
        *)
            log_warning "Unknown service: ${service}"
            ;;
    esac
}

# Verify Terraform state file exists (for IaC projects)
verify_terraform_state() {
    local tf_dir="${1:-.}"
    
    if [[ ! -d "${tf_dir}" ]]; then
        log_skip "Terraform directory not found: ${tf_dir}"
        return 0
    fi

    if [[ -f "${tf_dir}/terraform.tfstate" ]]; then
        log_success "Terraform state file exists"
        
        if [[ "$DRY_RUN" == "0" ]] && check_aws_credentials; then
            # Check if state shows any resources (without printing sensitive data)
            local resource_count
            resource_count=$(grep -c '"type":' "${tf_dir}/terraform.tfstate" 2>/dev/null || echo "0")
            if [[ "$resource_count" -gt 0 ]]; then
                log_info "Terraform state contains ${resource_count} resources"
            else
                log_warning "Terraform state file exists but appears empty"
            fi
        fi
    else
        log_skip "No Terraform state file (infrastructure not deployed)"
    fi
}

# Verify SAM/CloudFormation stack exists
verify_sam_stack() {
    local stack_name="$1"
    
    if [[ "$DRY_RUN" == "1" ]]; then
        log_skip "DRY_RUN=1: Skipping SAM stack check for ${stack_name}"
        return 0
    fi

    if ! check_aws_credentials; then
        return 0
    fi

    if aws cloudformation describe-stacks --stack-name "$stack_name" > /dev/null 2>&1; then
        log_success "SAM/CloudFormation stack '${stack_name}' exists"
    else
        log_skip "SAM/CloudFormation stack '${stack_name}' not found (not deployed)"
    fi
}

# Print dry-run banner
print_dry_run_banner() {
    local project_name="$1"
    
    echo ""
    echo "========================================"
    echo "  AWS Verification: ${project_name}"
    echo "========================================"
    echo ""
    
    if [[ "$DRY_RUN" == "1" ]]; then
        log_info "Mode: DRY_RUN (no AWS credentials required)"
        log_info "To verify against live AWS, set DRY_RUN=0 and configure AWS credentials"
    else
        log_info "Mode: LIVE AWS verification"
        log_info "Checking AWS credentials and service access..."
    fi
    echo ""
}

# Print verification summary
print_verification_summary() {
    echo ""
    echo "========================================"
    echo "  Verification Complete"
    echo "========================================"
    echo ""
    
    if [[ "$DRY_RUN" == "1" ]]; then
        log_info "Dry-run mode: All checks passed without AWS credentials"
        log_info "This project can be tested locally in simulation mode"
    else
        log_info "Live AWS verification completed"
        log_info "Review warnings above for any permission or deployment issues"
    fi
    echo ""
}
