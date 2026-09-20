# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-018-log-alb-access-i01 | Pattern: log-alb-access

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

resource "aws_lb" "this" {
  name               = "eval-log-018-log-alb-access-i01"
  internal           = true
  load_balancer_type = "application"
  subnets            = ["subnet-0evala", "subnet-0evalb"]
  security_groups    = ["sg-0evallb"]

  access_logs {
    bucket  = "eval-tf-log-018-log-alb-access-i01-alblogs"
    enabled = false
  }
  drop_invalid_header_fields = true
}
