# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: secure | Module: enc-021-enc-sns-s01 | Pattern: enc-sns

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

resource "aws_sns_topic" "this" {
  name              = "eval-enc-021-enc-sns-s01"
  kms_master_key_id = "alias/aws/sns"
}
