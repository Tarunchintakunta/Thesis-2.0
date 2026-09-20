# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: secure | Module: oa-016-oa-iam-star-s01 | Pattern: oa-iam-star

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

resource "aws_iam_policy" "this" {
  name        = "eval-oa-016-oa-iam-star-s01"
  description = "Evaluation IAM policy oa-016-oa-iam-star-s01"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "s3:GetObject"
      Resource = "arn:aws:s3:::eval-private/app/*"
    }]
  })
}
