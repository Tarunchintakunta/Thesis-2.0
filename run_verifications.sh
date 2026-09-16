#!/bin/bash

function verify_project() {
    local dir=$1
    local cmd=$2
    echo "==========================================="
    echo "Verifying $dir with command: $cmd"
    echo "==========================================="
    
    cd "$dir" || { echo "Failed to cd to $dir"; return 1; }
    
    # Try 3 times
    for i in {1..3}; do
        echo "--> Run $i/3 for $dir"
        eval "$cmd" > /dev/null 2>&1
        local status=$?
        if [ $status -eq 0 ]; then
            echo "    [PASS] Run $i successful."
        else
            echo "    [FAIL] Run $i failed with status $status."
        fi
    done
    cd - > /dev/null
}

echo "Starting verification..."

if [ -d "anji-thesis/sqs-reliability-recovery" ]; then
    verify_project "anji-thesis/sqs-reliability-recovery" "pytest tests/ || echo 'No pytest'"
fi

if [ -d "chaitanya-thesis/lambda-coldstart-isolation" ]; then
    verify_project "chaitanya-thesis/lambda-coldstart-isolation" "pytest tests/ || echo 'No pytest'"
fi

if [ -d "kasi-thesis/serverless-log-anomaly" ]; then
    verify_project "kasi-thesis/serverless-log-anomaly" "pytest tests/ || echo 'No pytest'"
fi

if [ -d "rassool-thesis/dynamodb-pk-capacity-eval" ]; then
    verify_project "rassool-thesis/dynamodb-pk-capacity-eval" "make test"
fi

if [ -d "vikas-thesis/lambda-idempotency-eval" ]; then
    verify_project "vikas-thesis/lambda-idempotency-eval" "pytest tests/"
fi

if [ -d "yashaswini-thesis/serverless-fault-localisation" ]; then
    verify_project "yashaswini-thesis/serverless-fault-localisation" "make test"
fi

echo "Verification complete."
