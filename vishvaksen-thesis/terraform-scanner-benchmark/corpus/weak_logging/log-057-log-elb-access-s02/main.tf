# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: secure | Module: log-057-log-elb-access-s02 | Pattern: log-elb-access

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

resource "aws_elb" "this" {
  name               = "eval-log-057-log-elb-access-s"
  availability_zones = ["eu-west-2a", "eu-west-2b"]
  internal           = true
  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }
  access_logs {
    bucket  = "eval-tf-log-057-log-elb-access-s02-elblogs"
    enabled = true
  }
  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:80/"
    interval            = 30
  }
}
