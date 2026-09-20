# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-059-enc-kinesis-i02 | Pattern: enc-kinesis

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

variable "encryption_type" {
  type    = string
  default = "NONE"
}

resource "aws_kinesis_stream" "this" {
  name            = "eval-enc-059-enc-kinesis-i02"
  shard_count     = 1
  encryption_type = var.encryption_type
  kms_key_id      = null
}
