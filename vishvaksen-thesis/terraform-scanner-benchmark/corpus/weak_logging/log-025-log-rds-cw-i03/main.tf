# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-025-log-rds-cw-i03 | Pattern: log-rds-cw

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

resource "aws_db_instance" "this" {
  identifier                     = "eval-log-025-log-rds-cw-i03"
  engine                         = "postgres"
  engine_version                 = "15"
  instance_class                 = "db.t3.micro"
  allocated_storage              = 20
  username                       = "evaladmin"
  manage_master_user_password    = true
  skip_final_snapshot            = true
  backup_retention_period        = 7
  storage_encrypted              = true
  publicly_accessible            = false
  enabled_cloudwatch_logs_exports = []
}
