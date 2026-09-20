# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: secure | Module: enc-017-enc-efs-s02 | Pattern: enc-efs

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

resource "aws_efs_file_system" "this" {
  encrypted  = true
  kms_key_id = "arn:aws:kms:{spec.region}:123456789012:key/eval"
}
