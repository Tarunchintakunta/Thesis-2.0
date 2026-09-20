# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: secure | Module: oa-026-oa-nacl-all-s01 | Pattern: oa-nacl-all

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

resource "aws_network_acl" "this" {
  vpc_id = "vpc-0evals01"
}

resource "aws_network_acl_rule" "ingress" {
  network_acl_id = aws_network_acl.this.id
  rule_number    = 100
  egress         = false
  protocol       = "6"
  rule_action    = "allow"
  cidr_block     = "10.0.0.0/16"
  from_port      = 443
  to_port        = 443
}
