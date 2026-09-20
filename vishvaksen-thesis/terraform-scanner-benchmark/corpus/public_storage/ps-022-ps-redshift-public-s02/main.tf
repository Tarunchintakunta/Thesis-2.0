# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: secure | Module: ps-022-ps-redshift-public-s02 | Pattern: ps-redshift-public

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

resource "aws_redshift_cluster" "this" {
  cluster_identifier  = "eval-ps-022-ps-redshift-public-s02"
  node_type           = "dc2.large"
  master_username     = "evaladmin"
  master_password     = var.master_password
  cluster_type        = "single-node"
  encrypted           = true
  publicly_accessible = false
  skip_final_snapshot = true
}

variable "master_password" {
  type      = string
  sensitive = true
}
