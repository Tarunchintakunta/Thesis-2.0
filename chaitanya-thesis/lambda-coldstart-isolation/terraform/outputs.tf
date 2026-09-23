output "name_prefix" {
  value = var.name_prefix
}

output "warmer_rule" {
  value = aws_cloudwatch_event_rule.warmer.name
}

output "function_names" {
  value = {
    for k, f in aws_lambda_function.fn : k => f.function_name
  }
}

output "role_arn" {
  value = aws_iam_role.fn.arn
}
