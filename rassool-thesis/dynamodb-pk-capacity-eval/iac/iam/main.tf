# Least-privilege roles/policies.
#  * driver role  - what the load-generator Lambda may do (data plane on the six tables only)
#  * operator policy - what the person running the matrix needs (output as JSON, attach it yourself)

variable "table_arns" {
  type = list(string)
}

variable "results_bucket_arn" {
  type = string
}

variable "function_name" {
  type = string
}

data "aws_caller_identity" "me" {}
data "aws_region" "here" {}

locals {
  log_group_arn = "arn:aws:logs:${data.aws_region.here.region}:${data.aws_caller_identity.me.account_id}:log-group:/aws/lambda/${var.function_name}"
  function_arn  = "arn:aws:lambda:${data.aws_region.here.region}:${data.aws_caller_identity.me.account_id}:function:${var.function_name}"
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

resource "aws_iam_role" "driver" {
  name_prefix        = "ddbpk-driver-"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

data "aws_iam_policy_document" "driver" {
  statement {
    sid = "TablesDataPlane"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:BatchGetItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:DescribeTable",
    ]
    resources = var.table_arns
  }

  statement {
    sid       = "RawResults"
    actions   = ["s3:PutObject"]
    resources = ["${var.results_bucket_arn}/raw/*"]
  }

  statement {
    sid       = "OwnLogs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${local.log_group_arn}:*"]
  }
}

resource "aws_iam_role_policy" "driver" {
  name   = "driver"
  role   = aws_iam_role.driver.id
  policy = data.aws_iam_policy_document.driver.json
}

data "aws_iam_policy_document" "operator" {
  statement {
    sid       = "InvokeDriver"
    actions   = ["lambda:InvokeFunction"]
    resources = [local.function_arn]
  }

  statement {
    sid       = "ReadTableState"
    actions   = ["dynamodb:DescribeTable"]
    resources = var.table_arns
  }

  statement {
    sid       = "Metrics"
    actions   = ["cloudwatch:GetMetricData", "application-autoscaling:DescribeScalingActivities"]
    resources = ["*"] # these APIs do not support resource-level permissions
  }

  statement {
    sid       = "DownloadRaw"
    actions   = ["s3:GetObject", "s3:ListBucket"]
    resources = [var.results_bucket_arn, "${var.results_bucket_arn}/raw/*"]
  }
}

output "driver_role_arn" {
  value = aws_iam_role.driver.arn
}

output "operator_policy_json" {
  value = data.aws_iam_policy_document.operator.json
}
