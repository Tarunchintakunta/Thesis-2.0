# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: secure | Module: oa-056-oa-secrets-policy-s01 | Pattern: oa-secrets-policy

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
  region = "eu-west-1"
}

resource "aws_secretsmanager_secret" "this" {
  name       = "eval-oa-056-oa-secrets-policy-s01"
  kms_key_id = "alias/aws/secretsmanager"
}

resource "aws_secretsmanager_secret_policy" "this" {
  secret_arn = aws_secretsmanager_secret.this.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = "arn:aws:iam::123456789012:root" }
      Action    = "secretsmanager:GetSecretValue"
      Resource  = "*"
    }]
  })
}
