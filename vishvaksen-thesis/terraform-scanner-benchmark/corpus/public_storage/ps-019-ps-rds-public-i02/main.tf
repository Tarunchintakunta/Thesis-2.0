# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: insecure | Module: ps-019-ps-rds-public-i02 | Pattern: ps-rds-public

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

variable "publicly_accessible" {
  type    = bool
  default = true
}

resource "aws_db_instance" "this" {
  identifier                   = "eval-ps-019-ps-rds-public-i02"
  engine                       = "mysql"
  engine_version               = "8.0"
  instance_class               = "db.t3.micro"
  allocated_storage            = 20
  username                     = "evaladmin"
  manage_master_user_password  = true
  skip_final_snapshot          = true
  backup_retention_period      = 7
  storage_encrypted            = true
  publicly_accessible          = var.publicly_accessible
  vpc_security_group_ids       = ["sg-0evaldb"]
}
