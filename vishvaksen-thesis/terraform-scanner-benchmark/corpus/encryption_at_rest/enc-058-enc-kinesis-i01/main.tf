# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-058-enc-kinesis-i01 | Pattern: enc-kinesis

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

resource "aws_kinesis_stream" "this" {
  name            = "eval-enc-058-enc-kinesis-i01"
  shard_count     = 1
  encryption_type = "NONE"
  kms_key_id      = null
}
