# One DynamoDB table and one Lambda function (master prompt 5 and 6). On-demand
# capacity, streams on (the independent record of every state change), no SDK
# or platform retries. `terraform destroy` removes all of it.

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      project = "lambda-idempotency-eval"
      student = "X25178849"
      data    = "synthetic"
    }
  }
}

resource "aws_dynamodb_table" "items" {
  name                        = var.table_name
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "pk"
  table_class                 = "STANDARD"
  stream_enabled              = true
  stream_view_type            = "NEW_AND_OLD_IMAGES"
  deletion_protection_enabled = false

  attribute {
    name = "pk"
    type = "S"
  }

  # P3 idempotency keys carry an epoch-seconds expiry, like Powertools does
  ttl {
    attribute_name = "expiry"
    enabled        = true
  }
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "fn" {
  name               = "${var.function_name}-role"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

data "aws_iam_policy_document" "fn" {
  statement {
    sid       = "WritePaths"
    actions   = ["dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:GetItem"]
    resources = [aws_dynamodb_table.items.arn]
  }

  statement {
    sid       = "Logs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.fn.arn}:*"]
  }
}

resource "aws_iam_role_policy" "fn" {
  name   = "write-paths"
  role   = aws_iam_role.fn.id
  policy = data.aws_iam_policy_document.fn.json
}

resource "aws_cloudwatch_log_group" "fn" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 14
}

resource "aws_lambda_function" "fn" {
  function_name                  = var.function_name
  role                           = aws_iam_role.fn.arn
  runtime                        = "python3.12"
  architectures                  = ["arm64"]
  handler                        = "lambda_fn.handler.lambda_handler"
  filename                       = var.lambda_package
  source_code_hash               = filebase64sha256(var.lambda_package)
  memory_size                    = var.memory_mb
  timeout                        = var.timeout_s
  reserved_concurrent_executions = var.reserved_concurrency

  environment {
    variables = {
      TABLE_NAME   = aws_dynamodb_table.items.name
      P3_KEY_TTL_S = tostring(var.p3_key_ttl_s)
      INJECT_MODE  = "sleep"
    }
  }

  depends_on = [aws_cloudwatch_log_group.fn, aws_iam_role_policy.fn]
}

# The driver only uses synchronous invokes, which Lambda does not retry. This
# makes sure an asynchronous invoke (by mistake) is not retried by the platform
# either, so every delivery in the data is a scheduled one.
resource "aws_lambda_function_event_invoke_config" "no_retries" {
  function_name          = aws_lambda_function.fn.function_name
  maximum_retry_attempts = 0
}
