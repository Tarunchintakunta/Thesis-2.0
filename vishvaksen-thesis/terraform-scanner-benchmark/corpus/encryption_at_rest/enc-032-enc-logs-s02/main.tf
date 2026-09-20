# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: secure | Module: enc-032-enc-logs-s02 | Pattern: enc-logs

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
  region = "eu-west-2"
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/eval/enc-032-enc-logs-s02"
  retention_in_days = 90
  kms_key_id        = "arn:aws:kms:eu-west-2:123456789012:key/eval"
}
