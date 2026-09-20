# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: insecure | Module: oa-045-oa-iam-s3-star-i03 | Pattern: oa-iam-s3-star

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

resource "aws_iam_user_policy" "this" {
  name = "eval-oa-045-oa-iam-s3-star-i03"
  user = aws_iam_user.this.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:*", "s3-object-lambda:*"]
      Resource = "arn:aws:s3:::eval-oa-045-oa-iam-s3-star-i03/*"
    }]
  })
}

resource "aws_iam_user" "this" {
  name = "eval-oa-045-oa-iam-s3-star-i03"
}
