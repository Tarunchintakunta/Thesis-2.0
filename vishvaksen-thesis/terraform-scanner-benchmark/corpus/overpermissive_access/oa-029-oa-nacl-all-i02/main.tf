# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: insecure | Module: oa-029-oa-nacl-all-i02 | Pattern: oa-nacl-all

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

variable "nacl_cidr" {
  type    = string
  default = "0.0.0.0/0"
}

resource "aws_network_acl" "this" {
  vpc_id = "vpc-0evali02"
}

resource "aws_network_acl_rule" "ingress" {
  network_acl_id = aws_network_acl.this.id
  rule_number    = 100
  egress         = false
  protocol       = "-1"
  rule_action    = "allow"
  cidr_block     = var.nacl_cidr
  from_port      = 0
  to_port        = 0
}
