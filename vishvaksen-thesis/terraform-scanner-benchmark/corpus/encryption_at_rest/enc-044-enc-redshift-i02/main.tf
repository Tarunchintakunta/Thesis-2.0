# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: insecure | Module: enc-044-enc-redshift-i02 | Pattern: enc-redshift

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

resource "aws_redshift_cluster" "this" {
  cluster_identifier  = "eval-enc-044-enc-redshift-i02"
  node_type           = "dc2.large"
  master_username     = "evaladmin"
  master_password     = var.master_password
  cluster_type        = "single-node"
  publicly_accessible = false
  encrypted           = var.encrypted
  skip_final_snapshot = true
}

variable "master_password" {
  type      = string
  sensitive = true
}
