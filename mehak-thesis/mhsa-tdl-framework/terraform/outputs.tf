output "telemetry_stream_name" {
  value = aws_kinesis_stream.telemetry.name
}

output "inference_function_name" {
  value = try(aws_lambda_function.prediction[0].function_name, null)
}

output "inference_role_arn" {
  value = aws_iam_role.inference.arn
}
