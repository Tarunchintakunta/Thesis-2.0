# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: secure | Module: enc-027-enc-sqs-s02 | Pattern: enc-sqs

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

resource "aws_sqs_queue" "this" {
  name                    = "eval-enc-027-enc-sqs-s02"
  sqs_managed_sse_enabled = true
}
