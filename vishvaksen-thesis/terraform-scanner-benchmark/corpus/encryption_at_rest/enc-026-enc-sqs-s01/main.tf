# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: secure | Module: enc-026-enc-sqs-s01 | Pattern: enc-sqs

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
  name                    = "eval-enc-026-enc-sqs-s01"
  sqs_managed_sse_enabled = true
}
