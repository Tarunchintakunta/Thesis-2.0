# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-024-log-rds-cw-i02 | Pattern: log-rds-cw

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

variable "log_exports" {
  type    = list(string)
  default = []
}

resource "aws_db_instance" "this" {
  identifier                     = "eval-log-024-log-rds-cw-i02"
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
  enabled_cloudwatch_logs_exports = var.log_exports
}
