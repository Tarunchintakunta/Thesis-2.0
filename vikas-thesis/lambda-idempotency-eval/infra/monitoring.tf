# Spend guards (master prompt 6, safety): alarms when a day has more invocations
# or write units than the whole campaign needs, and an optional monthly budget.
# Alerts go to e-mail only when alert_email is set.

resource "aws_sns_topic" "alerts" {
  count = var.alert_email == "" ? 0 : 1
  name  = "${var.function_name}-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.alert_email == "" ? 0 : 1
  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "invocations" {
  alarm_name          = "${var.function_name}-daily-invocations"
  alarm_description   = "More invocations in a day than the experiment budget allows"
  namespace           = "AWS/Lambda"
  metric_name         = "Invocations"
  dimensions          = { FunctionName = aws_lambda_function.fn.function_name }
  statistic           = "Sum"
  period              = 86400
  evaluation_periods  = 1
  threshold           = var.max_daily_invocations
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = aws_sns_topic.alerts[*].arn
}

resource "aws_cloudwatch_metric_alarm" "write_units" {
  alarm_name          = "${var.table_name}-daily-write-units"
  alarm_description   = "More write capacity units in a day than the experiment needs"
  namespace           = "AWS/DynamoDB"
  metric_name         = "ConsumedWriteCapacityUnits"
  dimensions          = { TableName = aws_dynamodb_table.items.name }
  statistic           = "Sum"
  period              = 86400
  evaluation_periods  = 1
  threshold           = var.max_daily_write_units
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = aws_sns_topic.alerts[*].arn
}

resource "aws_budgets_budget" "monthly" {
  count        = var.alert_email == "" ? 0 : 1
  name         = "${var.function_name}-monthly"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }
}
