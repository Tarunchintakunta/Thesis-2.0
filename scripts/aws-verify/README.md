# AWS Verification Scripts for Thesis 2.0 Projects

This directory contains AWS verification scripts for the Cloud Computing MSc thesis cohort projects. These scripts verify that projects claiming AWS artifacts can be tested both locally (simulation) and against live AWS resources when credentials are available.

## Purpose

Per GitHub issue #28, these scripts provide:

1. **Credential-safe verification**: Fail closed without credentials; never print secrets
2. **Dry-run mode**: Test without AWS credentials (default `DRY_RUN=1`)
3. **Live AWS mode**: Verify against real AWS resources when credentials are available (`DRY_RUN=0`)
4. **Per-project verification**: Individual scripts for each project's specific AWS services

## Usage

### Quick Start

Run all verification scripts in dry-run mode (no AWS credentials required):

```bash
# From repository root
bash scripts/aws-verify/run-all.sh
```

### Dry-Run Mode (Default)

Dry-run mode tests that projects can run in simulation mode without AWS credentials:

```bash
# Run all projects
DRY_RUN=1 bash scripts/aws-verify/run-all.sh

# Run individual project
DRY_RUN=1 bash scripts/aws-verify/varun-s3.sh
```

### Live AWS Mode

To verify against live AWS resources, set `DRY_RUN=0` and ensure AWS credentials are configured:

```bash
# Configure AWS credentials first
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_REGION="eu-west-1"  # or your preferred region

# Run verification against live AWS
DRY_RUN=0 bash scripts/aws-verify/run-all.sh

# Or individual project
DRY_RUN=0 bash scripts/aws-verify/rassool-dynamodb.sh
```

### Using Makefile Targets

Each project's Makefile now includes an `aws-verify` target:

```bash
# From a project directory
cd Varun/s3-predictive-optimization
make aws-verify

# With live AWS
DRY_RUN=0 make aws-verify
```

## Project Scripts

### AWS-Backed Projects

These projects claim AWS artifacts and support both simulation and live deployment:

| Project | Script | AWS Services | Simulation Mode |
|---------|--------|--------------|-----------------|
| Varun - S3 Optimization | `varun-s3.sh` | S3, CloudWatch | ✓ DRY_RUN |
| Rassool - DynamoDB | `rassool-dynamodb.sh` | DynamoDB, Lambda, S3 | ✓ moto/local |
| Chaitanya - Lambda | `chaitanya-lambda.sh` | Lambda, EventBridge | ✓ proxy benchmarks |
| Yashaswini - Fault Localization | `yashaswini-serverless.sh` | Lambda, CloudWatch, X-Ray | ✓ sim mode |
| Anji - SQS Reliability | `anji-sqs.sh` | SQS, Lambda | ✓ DRY_RUN |
| Vikas - Lambda Idempotency | `vikas-lambda.sh` | Lambda, DynamoDB, Kinesis | ✓ moto/functional |

### Non-AWS Projects

These projects do not use AWS (informational verification only):

| Project | Script | Notes |
|---------|--------|-------|
| Nemi - SecureFL | `nemi-securefl.sh` | Live lite EC2+S3+CW; destroy-after-round |
| Uday - IoT | `uday-iot.sh` | Simulation only, no live deployment |
| Venkat - Matrix | `venkat-matrix.sh` | Local benchmarking only |

### Excluded Projects

- **kasi-thesis**: Excluded per issue requirements

## What Gets Verified

Each verification script checks:

1. **Project structure**: Makefile, configuration files exist
2. **AWS credentials**: Available and valid (fail closed if missing)
3. **Service access**: Read-only checks for required AWS services
4. **Deployed resources**: Stack/infrastructure presence (in live mode)
5. **Simulation mode**: Dry-run or mock backend functionality
6. **Test execution**: Quick smoke test where applicable

## Security & Safety

These scripts are designed to be safe:

- **Never print secrets**: No credentials, keys, or tokens in output
- **Never commit secrets**: No writes to version control
- **Fail closed**: Without credentials, scripts report SKIP (not ERROR)
- **Read-only**: No resource creation or modification in verification
- **Redacted output**: Account IDs are partially redacted

## Common Library

`common.sh` provides shared utilities:

- `check_aws_credentials()`: Validates AWS access without exposing secrets
- `verify_service_access()`: Read-only service availability check
- `verify_terraform_state()`: Checks IaC deployment status
- `verify_sam_stack()`: Checks CloudFormation/SAM stack existence
- Log functions: `log_info`, `log_success`, `log_warning`, `log_error`, `log_skip`

## Integration with Project Makefiles

Each project Makefile now includes:

```makefile
.PHONY: aws-verify

aws-verify:
	@bash ../../scripts/aws-verify/<project-script>.sh
```

This allows:
```bash
make aws-verify          # Dry-run mode
DRY_RUN=0 make aws-verify  # Live AWS mode
```

## Reproducibility Alignment

These scripts align with the Cloud Computing MSc config-manual 70%+ reproducibility requirement:

- **Configuration-driven**: All projects use declarative config (YAML, Terraform)
- **Environment isolation**: Virtual environments, containerization
- **Documented setup**: Each project has CONFIGURATION_MANUAL.md or equivalent
- **Automated testing**: Pytest, functional tests, smoke tests
- **Cost controls**: Free tier guards, budget estimators, pilot sizing

## Troubleshooting

### "AWS CLI not installed"

Install AWS CLI:
```bash
# macOS
brew install awscli

# Ubuntu/Debian
sudo apt-get install awscli

# Or use pip
pip install awscli
```

### "No valid AWS credentials found"

This is expected in dry-run mode. To use live AWS:

1. Configure credentials:
   ```bash
   aws configure
   ```
   Or use environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID="..."
   export AWS_SECRET_ACCESS_KEY="..."
   export AWS_REGION="eu-west-1"
   ```

2. Verify:
   ```bash
   aws sts get-caller-identity
   ```

3. Run with live mode:
   ```bash
   DRY_RUN=0 bash scripts/aws-verify/run-all.sh
   ```

### Permission Errors

If you see "access check failed" warnings:

- Ensure your AWS user/role has necessary permissions
- Some projects need specific service policies (S3, Lambda, DynamoDB, etc.)
- Check project's CONFIGURATION_MANUAL.md for required IAM policies

### Script Execution Issues

Make scripts executable:
```bash
chmod +x scripts/aws-verify/*.sh
```

## References

- GitHub Issue #28: https://github.com/Tarunchintakunta/Thesis-2.0/issues/28
- AWS CLI Documentation: https://docs.aws.amazon.com/cli/
- Terraform Documentation: https://www.terraform.io/docs
- AWS SAM Documentation: https://docs.aws.amazon.com/serverless-application-model/

## Contributing

When adding a new AWS-backed project:

1. Create `scripts/aws-verify/<project-name>.sh`
2. Source `common.sh` for shared utilities
3. Add project-specific service checks
4. Add `aws-verify` target to project's Makefile
5. Update this README with project details
6. Test in both dry-run and live modes

## License

These scripts are part of the Thesis 2.0 repository and follow the same license terms.
