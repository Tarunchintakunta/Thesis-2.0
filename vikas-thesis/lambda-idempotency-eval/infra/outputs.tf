output "table_name" {
  value = aws_dynamodb_table.items.name
}

output "stream_arn" {
  value = aws_dynamodb_table.items.stream_arn
}

output "function_name" {
  value = aws_lambda_function.fn.function_name
}

output "log_group" {
  value = aws_cloudwatch_log_group.fn.name
}
