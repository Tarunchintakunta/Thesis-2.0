# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: insecure | Module: log-029-log-apigw-i02 | Pattern: log-apigw

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

variable "xray_tracing_enabled" {
  type    = bool
  default = false
}

resource "aws_api_gateway_rest_api" "this" {
  name = "eval-log-029-log-apigw-i02"
}

resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id
}

resource "aws_api_gateway_stage" "this" {
  rest_api_id           = aws_api_gateway_rest_api.this.id
  deployment_id         = aws_api_gateway_deployment.this.id
  stage_name            = "prod"
  xray_tracing_enabled  = var.xray_tracing_enabled
}
