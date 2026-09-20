# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-060-enc-kinesis-i03 | Pattern: enc-kinesis

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

resource "aws_kinesis_stream" "this" {
  name            = "eval-enc-060-enc-kinesis-i03"
  shard_count     = 1
  encryption_type = "NONE"
  kms_key_id      = null
}
