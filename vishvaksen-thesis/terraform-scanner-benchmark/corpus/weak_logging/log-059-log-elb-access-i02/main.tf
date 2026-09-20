# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-059-log-elb-access-i02 | Pattern: log-elb-access

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

variable "access_logs_enabled" {
  type    = bool
  default = false
}

resource "aws_elb" "this" {
  name               = "eval-log-059-log-elb-access-i"
  availability_zones = ["eu-central-1a", "eu-central-1b"]
  internal           = true
  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }
  access_logs {
    bucket  = "eval-tf-log-059-log-elb-access-i02-elblogs"
    enabled = var.access_logs_enabled
  }
  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:80/"
    interval            = 30
  }
}
