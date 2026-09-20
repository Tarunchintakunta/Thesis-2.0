# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: insecure | Module: ps-033-ps-sns-policy-i01 | Pattern: ps-sns-policy

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

resource "aws_sns_topic" "this" {
  name              = "eval-ps-033-ps-sns-policy-i01"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_sns_topic_policy" "this" {
  arn = aws_sns_topic.this.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "sns:Publish"
      Resource  = aws_sns_topic.this.arn
    }]
  })
}
