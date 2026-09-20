# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: weak_logging | Label: secure | Module: log-026-log-apigw-s01 | Pattern: log-apigw

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

resource "aws_api_gateway_rest_api" "this" {
  name = "eval-log-026-log-apigw-s01"
}

resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id
}

resource "aws_api_gateway_stage" "this" {
  rest_api_id           = aws_api_gateway_rest_api.this.id
  deployment_id         = aws_api_gateway_deployment.this.id
  stage_name            = "prod"
  xray_tracing_enabled  = true
}


resource "aws_api_gateway_method_settings" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  stage_name  = aws_api_gateway_stage.this.stage_name
  method_path = "*/*"
  settings {
    logging_level      = "INFO"
    data_trace_enabled = false
    metrics_enabled    = true
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.this.id}/prod"
  retention_in_days = 90
}
