output "function_name" {
  value = try(aws_lambda_function.python_default[0].function_name, null)
}
output "log_group" { value = aws_cloudwatch_log_group.python_default.name }
output "role_arn" { value = aws_iam_role.fn.arn }
