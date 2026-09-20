# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-024-enc-sns-i02 | Pattern: enc-sns

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

variable "kms_master_key_id" {
  type    = string
  default = ""
}

resource "aws_sns_topic" "this" {
  name              = "eval-enc-024-enc-sns-i02"
  kms_master_key_id = var.kms_master_key_id
}
