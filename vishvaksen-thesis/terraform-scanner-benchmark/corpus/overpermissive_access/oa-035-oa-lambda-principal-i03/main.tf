# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: insecure | Module: oa-035-oa-lambda-principal-i03 | Pattern: oa-lambda-principal

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
  region = "ap-southeast-1"
}

resource "aws_lambda_function" "this" {
  function_name = "eval-oa-035-oa-lambda-principal-i03"
  role          = "arn:aws:iam::123456789012:role/eval-lambda"
  handler       = "index.handler"
  runtime       = "python3.12"
  filename      = "placeholder.zip"
}

resource "aws_lambda_permission" "this" {
  statement_id  = "EvalInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "*"
}
