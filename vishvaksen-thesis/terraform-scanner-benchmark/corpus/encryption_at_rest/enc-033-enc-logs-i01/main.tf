# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-033-enc-logs-i01 | Pattern: enc-logs

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/eval/enc-033-enc-logs-i01"
  retention_in_days = 90
  kms_key_id        = null
}
