# The load-generator Lambda (workloads/lambda_handler/handler.py), arm64, Python 3.12.
# 15-minute timeout: one measured batch is at most 180 s plus the settling call.

variable "function_name" {
  type = string
}

variable "role_arn" {
  type = string
}

variable "package" {
  type = string
}

variable "memory" {
  type = number
}

variable "results_bucket" {
  type = string
}

resource "aws_cloudwatch_log_group" "driver" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 14
}

resource "aws_lambda_function" "driver" {
  function_name    = var.function_name
  role             = var.role_arn
  runtime          = "python3.12"
  architectures    = ["arm64"]
  handler          = "workloads.lambda_handler.handler.lambda_handler"
  filename         = var.package
  source_code_hash = filebase64sha256(var.package)
  memory_size      = var.memory
  timeout          = 900

  environment {
    variables = {
      RESULTS_BUCKET = var.results_bucket
    }
  }

  depends_on = [aws_cloudwatch_log_group.driver]
}

output "function_name" {
  value = aws_lambda_function.driver.function_name
}
