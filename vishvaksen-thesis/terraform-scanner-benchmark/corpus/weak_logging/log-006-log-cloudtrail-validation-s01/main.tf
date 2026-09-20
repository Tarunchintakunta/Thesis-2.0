# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: secure | Module: log-006-log-cloudtrail-validation-s01 | Pattern: log-cloudtrail-validation

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

resource "aws_cloudtrail" "this" {
  name                          = "eval-log-006-log-cloudtrail-validation-s01"
  s3_bucket_name                = "eval-tf-log-006-log-cloudtrail-validation-s01-trail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  enable_logging                = true
}
