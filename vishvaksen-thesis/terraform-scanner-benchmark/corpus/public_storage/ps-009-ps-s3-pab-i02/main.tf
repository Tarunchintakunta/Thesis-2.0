# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: insecure | Module: ps-009-ps-s3-pab-i02 | Pattern: ps-s3-pab

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

variable "restrict_public" {
  type    = bool
  default = false
}

resource "aws_s3_bucket" "this" {
  bucket = "eval-tf-ps-009-ps-s3-pab-i02"
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = var.restrict_public
  block_public_policy     = var.restrict_public
  ignore_public_acls      = var.restrict_public
  restrict_public_buckets = var.restrict_public
}
