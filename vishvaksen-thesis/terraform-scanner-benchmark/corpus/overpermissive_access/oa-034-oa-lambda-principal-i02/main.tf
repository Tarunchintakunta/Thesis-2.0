# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: overpermissive_access | Label: insecure | Module: oa-034-oa-lambda-principal-i02 | Pattern: oa-lambda-principal

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

variable "invoke_principal" {
  type    = string
  default = "*"
}

resource "aws_lambda_function" "this" {
  function_name = "eval-oa-034-oa-lambda-principal-i02"
  role          = "arn:aws:iam::123456789012:role/eval-lambda"
  handler       = "index.handler"
  runtime       = "python3.12"
  filename      = "placeholder.zip"
}

resource "aws_lambda_permission" "this" {
  statement_id  = "EvalInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = var.invoke_principal
}
