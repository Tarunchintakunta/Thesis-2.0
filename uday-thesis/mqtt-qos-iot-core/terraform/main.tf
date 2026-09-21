# Free-Tier-leaning AWS IoT Core + Rules + Lambda + DynamoDB scaffold.
# Project tags only (no personal IDs). DO NOT apply until READY_FOR_AWS.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Thesis      = "uday-mqtt-qos"
      Environment = "research"
      ManagedBy   = "terraform"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "project_name" {
  type    = string
  default = "mqtt-qos-iot-core"
}

variable "enable_apply" {
  description = "Safety latch. Must be true to create resources; default false documents that live AWS is not applied yet."
  type        = bool
  default     = false
}

locals {
  name_prefix = var.project_name
  topic       = "mqttqos/telemetry/#"
}

data "archive_file" "ingest_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/lambda_ingest/handler.py"
  output_path = "${path.module}/build/ingest.zip"
}

resource "aws_dynamodb_table" "delivered" {
  count = var.enable_apply ? 1 : 0

  name         = "${local.name_prefix}-delivered"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "msg_id"
  range_key    = "delivery_id"

  attribute {
    name = "msg_id"
    type = "S"
  }

  attribute {
    name = "delivery_id"
    type = "S"
  }

  attribute {
    name = "run_id"
    type = "S"
  }

  global_secondary_index {
    name            = "run_id-index"
    hash_key        = "run_id"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}

resource "aws_iam_role" "ingest_lambda" {
  count = var.enable_apply ? 1 : 0

  name = "${local.name_prefix}-ingest"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "ingest_lambda" {
  count = var.enable_apply ? 1 : 0

  name = "${local.name_prefix}-ingest"
  role = aws_iam_role.ingest_lambda[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["dynamodb:PutItem"]
        Resource = [aws_dynamodb_table.delivered[0].arn]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "ingest" {
  count = var.enable_apply ? 1 : 0

  function_name    = "${local.name_prefix}-ingest"
  role             = aws_iam_role.ingest_lambda[0].arn
  handler          = "handler.handler"
  runtime          = "python3.12"
  filename         = data.archive_file.ingest_zip.output_path
  source_code_hash = data.archive_file.ingest_zip.output_base64sha256
  memory_size      = 128
  timeout          = 10

  environment {
    variables = {
      DELIVERED_TABLE = aws_dynamodb_table.delivered[0].name
      TTL_SECONDS     = "1209600"
    }
  }
}

resource "aws_iot_topic_rule" "ingest" {
  count = var.enable_apply ? 1 : 0

  name        = replace("${local.name_prefix}_ingest", "-", "_")
  enabled     = true
  sql         = "SELECT *, topic() as iot_topic FROM '${local.topic}'"
  sql_version = "2016-03-23"

  lambda {
    function_arn = aws_lambda_function.ingest[0].arn
  }
}

resource "aws_lambda_permission" "iot_invoke" {
  count = var.enable_apply ? 1 : 0

  statement_id  = "AllowIoTInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest[0].function_name
  principal     = "iot.amazonaws.com"
  source_arn    = aws_iot_topic_rule.ingest[0].arn
}

resource "aws_iot_thing" "synthetic" {
  count = var.enable_apply ? 1 : 0

  name = "${local.name_prefix}-synthetic-01"
}

resource "aws_iot_policy" "synthetic_publish" {
  count = var.enable_apply ? 1 : 0

  name = "${local.name_prefix}-synthetic-publish"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["iot:Connect", "iot:Publish"]
      Resource = ["*"]
    }]
  })
}

output "note" {
  value = var.enable_apply ? "Resources created — destroy after campaign." : "Scaffold only; enable_apply=false (live AWS not applied)."
}

output "delivered_table_name" {
  value = try(aws_dynamodb_table.delivered[0].name, null)
}

output "ingest_lambda_name" {
  value = try(aws_lambda_function.ingest[0].function_name, null)
}
