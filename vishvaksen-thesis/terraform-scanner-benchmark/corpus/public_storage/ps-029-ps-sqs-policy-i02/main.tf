# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: insecure | Module: ps-029-ps-sqs-policy-i02 | Pattern: ps-sqs-policy

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
  region = "eu-central-1"
}

variable "principal" {
  type    = string
  default = "*"
}

resource "aws_sqs_queue" "this" {
  name                    = "eval-ps-029-ps-sqs-policy-i02"
  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue_policy" "this" {
  queue_url = aws_sqs_queue.this.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = var.principal
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.this.arn
    }]
  })
}
