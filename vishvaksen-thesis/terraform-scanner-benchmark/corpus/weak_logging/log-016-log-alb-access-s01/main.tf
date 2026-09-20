# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: secure | Module: log-016-log-alb-access-s01 | Pattern: log-alb-access

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

resource "aws_lb" "this" {
  name               = "eval-log-016-log-alb-access-s01"
  internal           = true
  load_balancer_type = "application"
  subnets            = ["subnet-0evala", "subnet-0evalb"]
  security_groups    = ["sg-0evallb"]

  access_logs {
    bucket  = "eval-tf-log-016-log-alb-access-s01-alblogs"
    enabled = true
  }
  drop_invalid_header_fields = true
}
