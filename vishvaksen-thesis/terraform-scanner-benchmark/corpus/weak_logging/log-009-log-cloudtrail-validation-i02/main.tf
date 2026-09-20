# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-009-log-cloudtrail-validation-i02 | Pattern: log-cloudtrail-validation

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

variable "enable_log_file_validation" {
  type    = bool
  default = false
}

resource "aws_cloudtrail" "this" {
  name                          = "eval-log-009-log-cloudtrail-validation-i02"
  s3_bucket_name                = "eval-tf-log-009-log-cloudtrail-validation-i02-trail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = var.enable_log_file_validation
  enable_logging                = true
}
