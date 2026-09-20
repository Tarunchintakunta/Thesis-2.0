# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: insecure | Module: oa-008-oa-sg-all-i01 | Pattern: oa-sg-all

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

resource "aws_security_group" "this" {
  name        = "eval-oa-008-oa-sg-all-i01"
  description = "Evaluation security group oa-008-oa-sg-all-i01"
  vpc_id      = "vpc-0evali01"

  ingress {
    description = "labelled ingress"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
