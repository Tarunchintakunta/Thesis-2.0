variable "prefix" { type = string }
variable "region" { type = string }
variable "lambda_zip" { type = string }
variable "lambda_zip_hash" { type = string }
variable "lambda_memory_mb" { type = number }
variable "lambda_timeout_s" { type = number }
variable "log_retention_days" { type = number }
variable "ttl_seconds" { type = number }
variable "telemetry_topic" { type = string }

data "aws_caller_identity" "current" {}

locals {
  account   = data.aws_caller_identity.current.account_id
  rule_name = replace("${var.prefix}_ingest", "-", "_")
}

resource "aws_dynamodb_table" "delivered" {
  name         = "${var.prefix}-delivered"
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

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = false
  }
}

data "aws_iam_policy_document" "assume_lambda" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ingest" {
  name               = "${var.prefix}-ingest"
  assume_role_policy = data.aws_iam_policy_document.assume_lambda.json
}

data "aws_iam_policy_document" "ingest" {
  statement {
    sid       = "Logs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.ingest.arn}:*"]
  }

  statement {
    sid       = "PutDelivered"
    actions   = ["dynamodb:PutItem"]
    resources = [aws_dynamodb_table.delivered.arn]
  }
}

resource "aws_iam_role_policy" "ingest" {
  name   = "ingest"
  role   = aws_iam_role.ingest.id
  policy = data.aws_iam_policy_document.ingest.json
}

resource "aws_cloudwatch_log_group" "ingest" {
  name              = "/aws/lambda/${var.prefix}-ingest"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "rule_errors" {
  name              = "/aws/iot/${var.prefix}-rule-errors"
  retention_in_days = var.log_retention_days
}

data "aws_iam_policy_document" "assume_iot" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["iot.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "rule" {
  name               = "${var.prefix}-iot-rule"
  assume_role_policy = data.aws_iam_policy_document.assume_iot.json
}

data "aws_iam_policy_document" "rule" {
  statement {
    sid       = "InvokeIngest"
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.ingest.arn]
  }

  statement {
    sid       = "RuleErrorLogs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.rule_errors.arn}:*"]
  }
}

resource "aws_iam_role_policy" "rule" {
  name   = "iot-rule"
  role   = aws_iam_role.rule.id
  policy = data.aws_iam_policy_document.rule.json
}

resource "aws_lambda_function" "ingest" {
  function_name    = "${var.prefix}-ingest"
  role             = aws_iam_role.ingest.arn
  runtime          = "python3.12"
  architectures    = ["arm64"]
  handler          = "handler.handler"
  filename         = var.lambda_zip
  source_code_hash = var.lambda_zip_hash
  memory_size      = var.lambda_memory_mb
  timeout          = var.lambda_timeout_s

  environment {
    variables = {
      DELIVERED_TABLE = aws_dynamodb_table.delivered.name
      TTL_SECONDS     = tostring(var.ttl_seconds)
    }
  }

  depends_on = [aws_cloudwatch_log_group.ingest]
}

resource "aws_lambda_permission" "iot" {
  statement_id  = "AllowIoTRule"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest.function_name
  principal     = "iot.amazonaws.com"
  source_arn    = "arn:aws:iot:${var.region}:${local.account}:rule/${local.rule_name}"
}

resource "aws_iot_topic_rule" "ingest" {
  name        = local.rule_name
  enabled     = true
  sql         = "SELECT *, timestamp() as broker_ts FROM '${var.telemetry_topic}'"
  sql_version = "2016-03-23"

  lambda {
    function_arn = aws_lambda_function.ingest.arn
  }

  error_action {
    cloudwatch_logs {
      log_group_name = aws_cloudwatch_log_group.rule_errors.name
      role_arn       = aws_iam_role.rule.arn
    }
  }
}

output "table_name" {
  value = aws_dynamodb_table.delivered.name
}

output "lambda_function_name" {
  value = aws_lambda_function.ingest.function_name
}

output "lambda_arn" {
  value = aws_lambda_function.ingest.arn
}

output "rule_name" {
  value = aws_iot_topic_rule.ingest.name
}
