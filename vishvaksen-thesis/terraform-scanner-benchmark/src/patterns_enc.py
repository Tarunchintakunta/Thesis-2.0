"""Encryption-at-rest Terraform patterns."""

from __future__ import annotations

from .common import EVAL_BANNER, compose, lit_or_var, tf_preamble


def _banner(spec) -> str:
    return EVAL_BANNER.format(
        category=spec.category,
        label=spec.label,
        module_id=spec.module_id,
        pattern_id=spec.pattern_id,
    )


def enc_s3(spec) -> str:
    if spec.label == "secure":
        enc_block = '''
resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}
'''
        varb = ""
    elif spec.mode == "variable":
        enc_block = '''
resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = var.sse_algorithm
    }
  }
}

variable "sse_algorithm" {
  type    = string
  default = "AES256"
}
'''
        # Variable default AES256 is still encrypted — for insecure we omit KMS
        # AND use a dummy algorithm scanners may still treat as encrypted.
        # True insecure: no encryption resource at all for direct/alternate.
        enc_block = ""
        varb = '''
variable "enable_sse" {
  type    = bool
  default = false
}
'''
    else:
        enc_block = ""
        varb = ""
    body = f'''
resource "aws_s3_bucket" "this" {{
  bucket = "eval-tf-{spec.module_id}"
}}

resource "aws_s3_bucket_public_access_block" "this" {{
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

{enc_block}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_ebs(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="encrypted",
    )
    body = f'''
resource "aws_ebs_volume" "this" {{
  availability_zone = "{spec.region}a"
  size              = 20
  type              = "gp3"
  encrypted         = {flag}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_rds(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="storage_encrypted",
    )
    body = f'''
resource "aws_db_instance" "this" {{
  identifier                  = "eval-{spec.module_id}"
  engine                      = "postgres"
  engine_version              = "15"
  instance_class              = "db.t3.micro"
  allocated_storage           = 20
  username                    = "evaladmin"
  manage_master_user_password = true
  skip_final_snapshot         = true
  backup_retention_period     = 7
  publicly_accessible         = false
  storage_encrypted           = {flag}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_efs(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="encrypted",
    )
    body = f'''
resource "aws_efs_file_system" "this" {{
  encrypted  = {flag}
  kms_key_id = { '"arn:aws:kms:{spec.region}:123456789012:key/eval"' if spec.label == "secure" else "null" }
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_sns(spec) -> str:
    if spec.label == "secure":
        kms = '"alias/aws/sns"'
        varb = ""
    elif spec.mode == "variable":
        kms = "var.kms_master_key_id"
        varb = '''
variable "kms_master_key_id" {
  type    = string
  default = ""
}
'''
    else:
        kms = "null"
        varb = ""
    body = f'''
resource "aws_sns_topic" "this" {{
  name              = "eval-{spec.module_id}"
  kms_master_key_id = {kms}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_sqs(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="sqs_managed_sse_enabled",
    )
    body = f'''
resource "aws_sqs_queue" "this" {{
  name                    = "eval-{spec.module_id}"
  sqs_managed_sse_enabled = {flag}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_logs(spec) -> str:
    if spec.label == "secure":
        kms = '"arn:aws:kms:{region}:123456789012:key/eval"'.format(region=spec.region)
        varb = ""
    elif spec.mode == "variable":
        kms = "var.kms_key_id"
        varb = '''
variable "kms_key_id" {
  type    = string
  default = ""
}
'''
    else:
        kms = "null"
        varb = ""
    body = f'''
resource "aws_cloudwatch_log_group" "this" {{
  name              = "/eval/{spec.module_id}"
  retention_in_days = 90
  kms_key_id        = {kms}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_dynamodb(spec) -> str:
    enabled, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="sse_enabled",
    )
    body = f'''
resource "aws_dynamodb_table" "this" {{
  name           = "eval-{spec.module_id}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  attribute {{
    name = "id"
    type = "S"
  }}
  point_in_time_recovery {{
    enabled = true
  }}
  server_side_encryption {{
    enabled = {enabled}
  }}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_redshift(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="encrypted",
    )
    body = f'''
resource "aws_redshift_cluster" "this" {{
  cluster_identifier  = "eval-{spec.module_id}"
  node_type           = "dc2.large"
  master_username     = "evaladmin"
  master_password     = var.master_password
  cluster_type        = "single-node"
  publicly_accessible = false
  encrypted           = {flag}
  skip_final_snapshot = true
}}

variable "master_password" {{
  type      = string
  sensitive = true
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_elasticache(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="at_rest_encryption_enabled",
    )
    body = f'''
resource "aws_elasticache_replication_group" "this" {{
  replication_group_id       = "eval-{spec.module_id}"
  description                = "eval {spec.module_id}"
  node_type                  = "cache.t3.micro"
  num_cache_clusters         = 1
  automatic_failover_enabled = false
  at_rest_encryption_enabled = {flag}
  transit_encryption_enabled = true
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_glue(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="sse_at_rest",
    )
    body = f'''
resource "aws_glue_data_catalog_encryption_settings" "this" {{
  data_catalog_encryption_settings {{
    encryption_at_rest {{
      catalog_encryption_mode = { '"SSE-KMS"' if spec.label == "secure" else '"DISABLED"' }
      sse_aws_kms_key_id      = { '"arn:aws:kms:{spec.region}:123456789012:key/eval"' if spec.label == "secure" else "null" }
    }}
    connection_password_encryption {{
      return_connection_password_encrypted = {flag}
    }}
  }}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def enc_kinesis(spec) -> str:
    enc_type, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure="KMS",
        insecure="NONE",
        insecure_alt="NONE",
        var_name="encryption_type",
    )
    body = f'''
resource "aws_kinesis_stream" "this" {{
  name            = "eval-{spec.module_id}"
  shard_count     = 1
  encryption_type = {enc_type}
  kms_key_id      = { '"alias/aws/kinesis"' if spec.label == "secure" else "null" }
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


PATTERNS = [
    ("enc-s3-sse", "S3 bucket missing SSE configuration", "HIGH", "aws_s3_bucket_server_side_encryption_configuration", enc_s3),
    ("enc-ebs", "EBS volume unencrypted", "HIGH", "aws_ebs_volume.encrypted", enc_ebs),
    ("enc-rds", "RDS storage_encrypted false", "HIGH", "aws_db_instance.storage_encrypted", enc_rds),
    ("enc-efs", "EFS filesystem unencrypted", "HIGH", "aws_efs_file_system.encrypted", enc_efs),
    ("enc-sns", "SNS topic without KMS", "MEDIUM", "aws_sns_topic.kms_master_key_id", enc_sns),
    ("enc-sqs", "SQS queue SSE disabled", "MEDIUM", "aws_sqs_queue.sqs_managed_sse_enabled", enc_sqs),
    ("enc-logs", "CloudWatch log group without KMS", "MEDIUM", "aws_cloudwatch_log_group.kms_key_id", enc_logs),
    ("enc-dynamodb", "DynamoDB SSE disabled", "HIGH", "aws_dynamodb_table.server_side_encryption", enc_dynamodb),
    ("enc-redshift", "Redshift cluster unencrypted", "HIGH", "aws_redshift_cluster.encrypted", enc_redshift),
    ("enc-elasticache", "ElastiCache at-rest encryption disabled", "HIGH", "aws_elasticache_replication_group.at_rest_encryption_enabled", enc_elasticache),
    ("enc-glue", "Glue catalog encryption disabled", "MEDIUM", "aws_glue_data_catalog_encryption_settings", enc_glue),
    ("enc-kinesis", "Kinesis stream encryption NONE", "HIGH", "aws_kinesis_stream.encryption_type", enc_kinesis),
]
