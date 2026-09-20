# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-008-log-cloudtrail-validation-i01 | Pattern: log-cloudtrail-validation

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

resource "aws_cloudtrail" "this" {
  name                          = "eval-log-008-log-cloudtrail-validation-i01"
  s3_bucket_name                = "eval-tf-log-008-log-cloudtrail-validation-i01-trail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = false
  enable_logging                = true
}
