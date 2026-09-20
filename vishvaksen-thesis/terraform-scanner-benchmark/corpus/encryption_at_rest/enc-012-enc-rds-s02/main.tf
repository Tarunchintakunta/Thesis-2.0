# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: encryption_at_rest | Label: secure | Module: enc-012-enc-rds-s02 | Pattern: enc-rds

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

resource "aws_db_instance" "this" {
  identifier                  = "eval-enc-012-enc-rds-s02"
  engine                      = "postgres"
  engine_version              = "15"
  instance_class              = "db.t3.micro"
  allocated_storage           = 20
  username                    = "evaladmin"
  manage_master_user_password = true
  skip_final_snapshot         = true
  backup_retention_period     = 7
  publicly_accessible         = false
  storage_encrypted           = true
}
