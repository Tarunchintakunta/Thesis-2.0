# Manual checklist (documented procedure)

This checklist is the formal “manual review” instrument. A reviewer inspects
**only** `main.tf` for the module, against the module’s labelled category.
Do not run scanners while filling the sheet. Do not deploy.

Tick **Fail** if any item in the category is true. Tick **Pass** if none are.

## public_storage

1. S3 ACL is `public-read`, `public-read-write`, or `authenticated-read`.
2. S3 public access block flags are `false`.
3. Bucket/queue/topic/repo/OpenSearch policy `Principal` is `*`.
4. `publicly_accessible = true` on RDS / Redshift / Neptune.
5. `associate_public_ip_address = true` on EC2.
6. AMI launch permission `group = "all"`.

## overpermissive_access

1. Security-group or NACL ingress from `0.0.0.0/0` or `::/0`.
2. IAM `Action` and/or `Resource` is `*`, or `s3:*` on a user policy.
3. Managed policy `AdministratorAccess` or `IAMFullAccess`.
4. Lambda permission `principal = "*"`.
5. KMS / Secrets Manager policy principal `*`.
6. EKS `public_access_cidrs` includes `0.0.0.0/0`.

## encryption_at_rest

1. `encrypted` / `storage_encrypted` / `sqs_managed_sse_enabled` /
   `at_rest_encryption_enabled` is `false`.
2. S3 bucket has no `aws_s3_bucket_server_side_encryption_configuration`.
3. SNS / log group `kms_*` is `null` or empty.
4. DynamoDB `server_side_encryption.enabled = false`.
5. Glue `catalog_encryption_mode = "DISABLED"`.
6. Kinesis `encryption_type = "NONE"`.

## weak_logging

1. CloudTrail `enable_log_file_validation = false`, or no trail when the
   module is a trail-presence fixture.
2. VPC without `aws_flow_log`.
3. ALB/ELB `access_logs.enabled = false`.
4. RDS `enabled_cloudwatch_logs_exports = []`.
5. EKS `enabled_cluster_log_types = []`.
6. S3 without `aws_s3_bucket_logging` (unless the fixture is a trail/LB).
7. API Gateway stage without method settings.
8. WAF ACL without logging configuration.
9. Redshift `logging.enable = false` or MSK broker logs disabled.

## How this pass applies it

`scripts/run_checklist.py` implements the items as **regular expressions on
HCL text**. That is a scripted procedure, not an independent human rater.
Variable-indirection (`var.*`) is not ticked as a defect unless the literal
also appears (typically in the variable default — the script does not parse
defaults). Dual-reviewer agreement is **not** measured here.

Do not cite checklist figures as human-review accuracy.
