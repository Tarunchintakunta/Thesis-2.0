# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: secure | Module: ps-026-ps-sqs-policy-s01 | Pattern: ps-sqs-policy

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

resource "aws_sqs_queue" "this" {
  name                    = "eval-ps-026-ps-sqs-policy-s01"
  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue_policy" "this" {
  queue_url = aws_sqs_queue.this.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "arn:aws:iam::123456789012:root"
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.this.arn
    }]
  })
}
