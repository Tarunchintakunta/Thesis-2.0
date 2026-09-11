# CloudWatch dashboard for the six tables, a throttle-storm alarm per table
# (the abort condition in RUNBOOK.md) and an optional AWS Budgets alert.

variable "tables" {
  description = "configuration id => table name"
  type        = map(string)
}

variable "function_name" {
  type = string
}

variable "region" {
  type = string
}

variable "monthly_budget_usd" {
  type = number
}

variable "budget_email" {
  type = string
}

locals {
  table_widgets = [
    for id, name in var.tables : {
      type   = "metric"
      width  = 12
      height = 6
      properties = {
        title  = id
        region = var.region
        stat   = "Sum"
        period = 60
        metrics = [
          ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", name],
          [".", "ConsumedWriteCapacityUnits", ".", "."],
          [".", "ReadThrottleEvents", ".", "."],
          [".", "WriteThrottleEvents", ".", "."],
          [".", "ProvisionedReadCapacityUnits", ".", ".", { stat = "Average" }],
          [".", "ProvisionedWriteCapacityUnits", ".", ".", { stat = "Average" }],
        ]
      }
    }
  ]
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "ddbpk"
  dashboard_body = jsonencode({
    widgets = concat(local.table_widgets, [{
      type   = "metric"
      width  = 24
      height = 6
      properties = {
        title   = "driver Lambda"
        region  = var.region
        period  = 60
        stat    = "Sum"
        metrics = [["AWS/Lambda", "Invocations", "FunctionName", var.function_name], [".", "Errors", ".", "."]]
      }
    }])
  })
}

resource "aws_cloudwatch_metric_alarm" "throttle_storm" {
  for_each            = var.tables
  alarm_name          = "${each.value}-throttle-storm"
  alarm_description   = "More than 5,000 throttle events a minute for 3 minutes - stop the matrix (RUNBOOK abort rule)"
  comparison_operator = "GreaterThanThreshold"
  threshold           = 5000
  evaluation_periods  = 3
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "total"
    expression  = "reads + writes"
    label       = "throttle events"
    return_data = true
  }

  metric_query {
    id = "reads"
    metric {
      namespace   = "AWS/DynamoDB"
      metric_name = "ReadThrottleEvents"
      dimensions  = { TableName = each.value }
      period      = 60
      stat        = "Sum"
    }
  }

  metric_query {
    id = "writes"
    metric {
      namespace   = "AWS/DynamoDB"
      metric_name = "WriteThrottleEvents"
      dimensions  = { TableName = each.value }
      period      = 60
      stat        = "Sum"
    }
  }
}

resource "aws_budgets_budget" "spend" {
  count        = var.budget_email == "" ? 0 : 1
  name         = "ddbpk-monthly"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.budget_email]
  }
}

output "dashboard_name" {
  value = aws_cloudwatch_dashboard.main.dashboard_name
}
