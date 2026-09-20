# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-043-log-redshift-audit-i01 | Pattern: log-redshift-audit

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

resource "aws_redshift_cluster" "this" {
  cluster_identifier  = "eval-log-043-log-redshift-audit-i01"
  node_type           = "dc2.large"
  master_username     = "evaladmin"
  master_password     = var.master_password
  cluster_type        = "single-node"
  publicly_accessible = false
  encrypted           = true
  skip_final_snapshot = true
  logging {
    enable        = false
    bucket_name   = "eval-tf-log-043-log-redshift-audit-i01-rslogs"
    s3_key_prefix = "redshift/"
  }
}

variable "master_password" {
  type      = string
  sensitive = true
}
