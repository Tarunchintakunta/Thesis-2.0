# Tags: project slug only — never personal name or personal ID.
provider "aws" {
  region = var.region
  default_tags {
    tags = {
      project    = "lambda-coldstart-isolation"
      managed_by = "terraform"
      purpose    = "research-eval"
      data       = "synthetic"
    }
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
  name               = "${var.name_prefix}-fn"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.fn.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_cloudwatch_log_group" "python_default" {
  name              = "/aws/lambda/${var.name_prefix}-python-default"
  retention_in_days = 7
}

resource "aws_lambda_function" "python_default" {
  count = fileexists(var.lambda_package) ? 1 : 0

  function_name    = "${var.name_prefix}-python-default"
  role             = aws_iam_role.fn.arn
  runtime          = "python3.12"
  architectures    = ["arm64"]
  handler          = "handler.lambda_handler"
  filename         = var.lambda_package
  source_code_hash = filebase64sha256(var.lambda_package)
  memory_size      = var.memory_mb
  timeout          = 30

  environment {
    variables = {
      COLD_TOKEN = "initial"
    }
  }

  depends_on = [aws_cloudwatch_log_group.python_default]
}

resource "aws_cloudwatch_log_metric_filter" "init_duration" {
  name           = "${var.name_prefix}-init-duration"
  log_group_name = aws_cloudwatch_log_group.python_default.name
  pattern        = "REPORT"

  metric_transformation {
    name      = "InitDurationReports"
    namespace = "ColdStartIsolation"
    value     = "1"
  }
}
