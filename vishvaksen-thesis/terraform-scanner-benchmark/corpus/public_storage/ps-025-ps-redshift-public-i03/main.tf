# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: insecure | Module: ps-025-ps-redshift-public-i03 | Pattern: ps-redshift-public

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
  region = "ap-southeast-1"
}

resource "aws_redshift_cluster" "this" {
  cluster_identifier  = "eval-ps-025-ps-redshift-public-i03"
  node_type           = "dc2.large"
  master_username     = "evaladmin"
  master_password     = var.master_password
  cluster_type        = "single-node"
  encrypted           = true
  publicly_accessible = true
  skip_final_snapshot = true
}

variable "master_password" {
  type      = string
  sensitive = true
}
