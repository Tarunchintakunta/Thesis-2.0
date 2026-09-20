# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: insecure | Module: oa-040-oa-kms-policy-i03 | Pattern: oa-kms-policy

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
  region = "ap-southeast-1"
}

resource "aws_kms_key" "this" {
  description             = "eval oa-040-oa-kms-policy-i03"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "EvalKey"
      Effect    = "Allow"
      Principal = { AWS = "*" }
      Action    = "kms:*"
      Resource  = "*"
    }]
  })
}
