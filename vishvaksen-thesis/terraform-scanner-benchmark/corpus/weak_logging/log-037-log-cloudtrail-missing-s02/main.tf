# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: secure | Module: log-037-log-cloudtrail-missing-s02 | Pattern: log-cloudtrail-missing

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

resource "aws_s3_bucket" "this" {
  bucket = "eval-tf-log-037-log-cloudtrail-missing-s02"
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_cloudtrail" "this" {
  name                          = "eval-log-037-log-cloudtrail-missing-s02"
  s3_bucket_name                = "eval-tf-log-037-log-cloudtrail-missing-s02-trail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  enable_logging                = true
}
