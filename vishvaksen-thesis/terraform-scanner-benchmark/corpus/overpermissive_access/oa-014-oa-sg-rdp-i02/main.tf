# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: insecure | Module: oa-014-oa-sg-rdp-i02 | Pattern: oa-sg-rdp

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

variable "rdp_cidr" {
  type    = string
  default = "0.0.0.0/0"
}

resource "aws_security_group" "this" {
  name        = "eval-oa-014-oa-sg-rdp-i02"
  description = "Evaluation security group oa-014-oa-sg-rdp-i02"
  vpc_id      = "vpc-0evali02"

  ingress {
    description = "labelled ingress"
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = [var.rdp_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
