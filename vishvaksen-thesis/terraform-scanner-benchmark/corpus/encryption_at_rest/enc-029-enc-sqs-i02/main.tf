# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-029-enc-sqs-i02 | Pattern: enc-sqs

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

variable "sqs_managed_sse_enabled" {
  type    = bool
  default = false
}

resource "aws_sqs_queue" "this" {
  name                    = "eval-enc-029-enc-sqs-i02"
  sqs_managed_sse_enabled = var.sqs_managed_sse_enabled
}
