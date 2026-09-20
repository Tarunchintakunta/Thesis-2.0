# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: public_storage | Label: secure | Module: ps-016-ps-rds-public-s01 | Pattern: ps-rds-public

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

resource "aws_db_instance" "this" {
  identifier                   = "eval-ps-016-ps-rds-public-s01"
  engine                       = "mysql"
  engine_version               = "8.0"
  instance_class               = "db.t3.micro"
  allocated_storage            = 20
  username                     = "evaladmin"
  manage_master_user_password  = true
  skip_final_snapshot          = true
  backup_retention_period      = 7
  storage_encrypted            = true
  publicly_accessible          = false
  vpc_security_group_ids       = ["sg-0evaldb"]
}
