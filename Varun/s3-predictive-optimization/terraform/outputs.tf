output "bucket_name" { value = aws_s3_bucket.eval.id }
output "bucket_arn" { value = aws_s3_bucket.eval.arn }
output "log_group" { value = aws_cloudwatch_log_group.runner.name }
output "runner_role_arn" { value = aws_iam_role.runner.arn }
output "runner_instance_profile" { value = aws_iam_instance_profile.runner.name }
