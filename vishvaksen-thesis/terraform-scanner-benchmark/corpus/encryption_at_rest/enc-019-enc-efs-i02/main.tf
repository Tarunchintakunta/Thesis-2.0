# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-019-enc-efs-i02 | Pattern: enc-efs

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

variable "encrypted" {
  type    = bool
  default = false
}

resource "aws_efs_file_system" "this" {
  encrypted  = var.encrypted
  kms_key_id = null
}
