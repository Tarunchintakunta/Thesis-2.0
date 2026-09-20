# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: secure | Module: ps-056-ps-neptune-public-s01 | Pattern: ps-neptune-public

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

resource "aws_neptune_cluster" "this" {
  cluster_identifier                   = "eval-ps-056-ps-neptune-public-s01"
  engine                               = "neptune"
  backup_retention_period              = 7
  skip_final_snapshot                  = true
  storage_encrypted                    = true
  iam_database_authentication_enabled  = true
}

resource "aws_neptune_cluster_instance" "this" {
  identifier          = "eval-ps-056-ps-neptune-public-s01-i"
  cluster_identifier  = aws_neptune_cluster.this.id
  instance_class      = "db.t3.medium"
  publicly_accessible = false
}
