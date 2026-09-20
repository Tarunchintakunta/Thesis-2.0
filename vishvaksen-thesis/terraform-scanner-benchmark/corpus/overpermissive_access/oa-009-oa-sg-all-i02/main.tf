# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: insecure | Module: oa-009-oa-sg-all-i02 | Pattern: oa-sg-all

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

variable "all_cidr" {
  type    = string
  default = "0.0.0.0/0"
}

resource "aws_security_group" "this" {
  name        = "eval-oa-009-oa-sg-all-i02"
  description = "Evaluation security group oa-009-oa-sg-all-i02"
  vpc_id      = "vpc-0evali02"

  ingress {
    description = "labelled ingress"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.all_cidr]
  }
}
