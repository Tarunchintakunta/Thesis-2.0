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

locals {
  functions = {
    python_default = {
      key     = "python-default"
      runtime = "python3.12"
      handler = "handler.lambda_handler"
      package = var.python_default_package
    }
    python_optimised = {
      key     = "python-optimised"
      runtime = "python3.12"
      handler = "handler.lambda_handler"
      package = var.python_optimised_package
    }
    nodejs_default = {
      key     = "nodejs-default"
      runtime = "nodejs20.x"
      handler = "index.handler"
      package = var.nodejs_default_package
    }
    nodejs_optimised = {
      key     = "nodejs-optimised"
      runtime = "nodejs20.x"
      handler = "index.handler"
      package = var.nodejs_optimised_package
    }
    java_default = {
      key     = "java-default"
      runtime = "java21"
      handler = "coldstart.Handler::handleRequest"
      package = var.java_default_package
    }
    java_optimised = {
      key     = "java-optimised"
      runtime = "java21"
      handler = "coldstart.Handler::handleRequest"
      package = var.java_optimised_package
    }
    warm_target = {
      key     = "warm-target"
      runtime = "python3.12"
      handler = "handler.lambda_handler"
      package = var.python_optimised_package
    }
    warm_control = {
      key     = "warm-control"
      runtime = "python3.12"
      handler = "handler.lambda_handler"
      package = var.python_optimised_package
    }
  }
  packages_ready = alltrue([
    for k, f in local.functions : fileexists(f.package)
  ])
}

resource "aws_cloudwatch_log_group" "fn" {
  for_each = local.functions

  name              = "/aws/lambda/${var.name_prefix}-${each.value.key}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "fn" {
  for_each = local.packages_ready ? local.functions : {}

  function_name    = "${var.name_prefix}-${each.value.key}"
  role             = aws_iam_role.fn.arn
  runtime          = each.value.runtime
  architectures    = ["arm64"]
  handler          = each.value.handler
  filename         = each.value.package
  source_code_hash = filebase64sha256(each.value.package)
  memory_size      = var.memory_mb
  timeout          = 30
  tracing_config {
    mode = var.enable_tracing ? "Active" : "PassThrough"
  }

  environment {
    variables = {
      COLD_TOKEN = "initial"
    }
  }

  depends_on = [aws_cloudwatch_log_group.fn]
}

# Low-frequency warmer (H3). DISABLED by default; LiveBackend enables during warming phase.
resource "aws_cloudwatch_event_rule" "warmer" {
  name                = "${var.name_prefix}-warmer"
  schedule_expression = var.warming_schedule
  state               = "DISABLED"
}

resource "aws_cloudwatch_event_target" "warmer" {
  count = local.packages_ready ? 1 : 0

  rule  = aws_cloudwatch_event_rule.warmer.name
  arn   = aws_lambda_function.fn["warm_target"].arn
  input = jsonencode({ warmer = true })
}

resource "aws_lambda_permission" "warmer" {
  count = local.packages_ready ? 1 : 0

  statement_id  = "AllowEventBridgeWarmer"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fn["warm_target"].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.warmer.arn
}
