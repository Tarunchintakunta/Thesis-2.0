# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: secure | Module: enc-057-enc-kinesis-s02 | Pattern: enc-kinesis

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

resource "aws_kinesis_stream" "this" {
  name            = "eval-enc-057-enc-kinesis-s02"
  shard_count     = 1
  encryption_type = "KMS"
  kms_key_id      = "alias/aws/kinesis"
}
