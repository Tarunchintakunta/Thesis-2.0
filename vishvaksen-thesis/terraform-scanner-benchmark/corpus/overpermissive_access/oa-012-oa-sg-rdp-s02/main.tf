# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: secure | Module: oa-012-oa-sg-rdp-s02 | Pattern: oa-sg-rdp

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

resource "aws_security_group" "this" {
  name        = "eval-oa-012-oa-sg-rdp-s02"
  description = "Evaluation security group oa-012-oa-sg-rdp-s02"
  vpc_id      = "vpc-0evals02"

  ingress {
    description = "labelled ingress"
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
