#!/usr/bin/env bash
# Master AWS verification runner
# Runs all per-project verification scripts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "  Master AWS Verification Runner"
echo "  Thesis 2.0 Cohort Projects"
echo "========================================"
echo ""
echo "DRY_RUN=${DRY_RUN:-1} (set to 0 for live AWS checks)"
echo ""

FAILED=0
PASSED=0

# Function to run a verification script
run_verification() {
    local script="$1"
    local name="$2"
    
    echo ""
    echo "----------------------------------------"
    echo "Running: ${name}"
    echo "----------------------------------------"
    
    if bash "${SCRIPT_DIR}/${script}"; then
        PASSED=$((PASSED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
}

# AWS-backed projects
run_verification "varun-s3.sh" "Varun - S3"
run_verification "rassool-dynamodb.sh" "Rassool - DynamoDB"
run_verification "chaitanya-lambda.sh" "Chaitanya - Lambda"
run_verification "yashaswini-serverless.sh" "Yashaswini - Serverless"
run_verification "anji-sqs.sh" "Anji - SQS"
run_verification "vikas-lambda.sh" "Vikas - Lambda"

# Non-AWS projects (informational)
run_verification "nemi-securefl.sh" "Nemi - SecureFL"
run_verification "uday-iot.sh" "Uday - IoT"
run_verification "venkat-matrix.sh" "Venkat - Matrix"

# Summary
echo ""
echo "========================================"
echo "  Overall Summary"
echo "========================================"
echo ""
echo "Passed: ${PASSED}"
echo "Failed: ${FAILED}"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo "✓ All verifications completed successfully"
    exit 0
else
    echo "✗ Some verifications failed (see above for details)"
    exit 1
fi
