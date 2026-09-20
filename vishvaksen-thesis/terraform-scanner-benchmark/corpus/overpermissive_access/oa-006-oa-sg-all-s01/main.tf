# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: secure | Module: oa-006-oa-sg-all-s01 | Pattern: oa-sg-all

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

resource "aws_security_group" "this" {
  name        = "eval-oa-006-oa-sg-all-s01"
  description = "Evaluation security group oa-006-oa-sg-all-s01"
  vpc_id      = "vpc-0evals01"

  ingress {
    description = "labelled ingress"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
}
