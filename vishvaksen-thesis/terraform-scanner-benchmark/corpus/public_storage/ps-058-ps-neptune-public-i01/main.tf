# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: insecure | Module: ps-058-ps-neptune-public-i01 | Pattern: ps-neptune-public

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

resource "aws_neptune_cluster" "this" {
  cluster_identifier                   = "eval-ps-058-ps-neptune-public-i01"
  engine                               = "neptune"
  backup_retention_period              = 7
  skip_final_snapshot                  = true
  storage_encrypted                    = true
  iam_database_authentication_enabled  = true
}

resource "aws_neptune_cluster_instance" "this" {
  identifier          = "eval-ps-058-ps-neptune-public-i01-i"
  cluster_identifier  = aws_neptune_cluster.this.id
  instance_class      = "db.t3.medium"
  publicly_accessible = true
}
