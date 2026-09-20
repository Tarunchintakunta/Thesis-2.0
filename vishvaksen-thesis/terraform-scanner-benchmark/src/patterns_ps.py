"""Public storage / public exposure Terraform patterns."""

from __future__ import annotations

from .common import EVAL_BANNER, compose, lit_or_var, tf_preamble


def _banner(spec) -> str:
    return EVAL_BANNER.format(
        category=spec.category,
        label=spec.label,
        module_id=spec.module_id,
        pattern_id=spec.pattern_id,
    )


def ps_s3_acl(spec) -> str:
    acl, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure="private",
        insecure="public-read",
        insecure_alt="public-read-write",
        var_name="bucket_acl",
    )
    pab = "true" if spec.label == "secure" else "false"
    body = f'''
resource "aws_s3_bucket" "this" {{
  bucket = "eval-tf-{spec.module_id}"
}}

resource "aws_s3_bucket_ownership_controls" "this" {{
  bucket = aws_s3_bucket.this.id
  rule {{
    object_ownership = "BucketOwnerPreferred"
  }}
}}

resource "aws_s3_bucket_acl" "this" {{
  bucket     = aws_s3_bucket.this.id
  acl        = {acl}
  depends_on = [aws_s3_bucket_ownership_controls.this]
}}

resource "aws_s3_bucket_public_access_block" "this" {{
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = {pab}
  block_public_policy     = {pab}
  ignore_public_acls      = {pab}
  restrict_public_buckets = {pab}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_s3_public_access_block(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="restrict_public",
    )
    body = f'''
resource "aws_s3_bucket" "this" {{
  bucket = "eval-tf-{spec.module_id}"
}}

resource "aws_s3_bucket_public_access_block" "this" {{
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = {flag}
  block_public_policy     = {flag}
  ignore_public_acls      = {flag}
  restrict_public_buckets = {flag}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_s3_bucket_policy(spec) -> str:
    if spec.label == "secure":
        principal = '"arn:aws:iam::123456789012:root"'
        varb = ""
    elif spec.mode == "variable":
        principal = "var.principal"
        varb = '''
variable "principal" {
  type    = string
  default = "*"
}
'''
    else:
        principal = '"*"'
        varb = ""
    action = '"s3:GetObject"' if spec.mode != "alternate" else '"s3:*"'
    body = f'''
resource "aws_s3_bucket" "this" {{
  bucket = "eval-tf-{spec.module_id}"
}}

resource "aws_s3_bucket_public_access_block" "this" {{
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = { "true" if spec.label == "secure" else "false" }
  block_public_policy     = { "true" if spec.label == "secure" else "false" }
  ignore_public_acls      = { "true" if spec.label == "secure" else "false" }
  restrict_public_buckets = { "true" if spec.label == "secure" else "false" }
}}

resource "aws_s3_bucket_policy" "this" {{
  bucket = aws_s3_bucket.this.id
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Sid       = "EvalObjectRead"
      Effect    = "Allow"
      Principal = {principal}
      Action    = {action}
      Resource  = "${{aws_s3_bucket.this.arn}}/*"
    }}]
  }})
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_rds_public(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=False,
        insecure=True,
        insecure_alt=True,
        var_name="publicly_accessible",
    )
    body = f'''
resource "aws_db_instance" "this" {{
  identifier                   = "eval-{spec.module_id}"
  engine                       = "mysql"
  engine_version               = "8.0"
  instance_class               = "db.t3.micro"
  allocated_storage            = 20
  username                     = "evaladmin"
  manage_master_user_password  = true
  skip_final_snapshot          = true
  backup_retention_period      = 7
  storage_encrypted            = true
  publicly_accessible          = {flag}
  vpc_security_group_ids       = ["sg-0evaldb"]
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_redshift_public(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=False,
        insecure=True,
        insecure_alt=True,
        var_name="publicly_accessible",
    )
    body = f'''
resource "aws_redshift_cluster" "this" {{
  cluster_identifier  = "eval-{spec.module_id}"
  node_type           = "dc2.large"
  master_username     = "evaladmin"
  master_password     = var.master_password
  cluster_type        = "single-node"
  encrypted           = true
  publicly_accessible = {flag}
  skip_final_snapshot = true
}}

variable "master_password" {{
  type      = string
  sensitive = true
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_sqs_policy(spec) -> str:
    if spec.label == "secure":
        principal = '"arn:aws:iam::123456789012:root"'
        varb = ""
    elif spec.mode == "variable":
        principal = "var.principal"
        varb = '''
variable "principal" {
  type    = string
  default = "*"
}
'''
    else:
        principal = '"*"'
        varb = ""
    body = f'''
resource "aws_sqs_queue" "this" {{
  name                    = "eval-{spec.module_id}"
  sqs_managed_sse_enabled = true
}}

resource "aws_sqs_queue_policy" "this" {{
  queue_url = aws_sqs_queue.this.id
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect    = "Allow"
      Principal = {principal}
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.this.arn
    }}]
  }})
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_sns_policy(spec) -> str:
    if spec.label == "secure":
        principal = '"arn:aws:iam::123456789012:root"'
        varb = ""
    elif spec.mode == "variable":
        principal = "var.principal"
        varb = '''
variable "principal" {
  type    = string
  default = "*"
}
'''
    else:
        principal = '"*"'
        varb = ""
    body = f'''
resource "aws_sns_topic" "this" {{
  name              = "eval-{spec.module_id}"
  kms_master_key_id = "alias/aws/sns"
}}

resource "aws_sns_topic_policy" "this" {{
  arn = aws_sns_topic.this.arn
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect    = "Allow"
      Principal = {principal}
      Action    = "sns:Publish"
      Resource  = aws_sns_topic.this.arn
    }}]
  }})
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_ecr_policy(spec) -> str:
    if spec.label == "secure":
        principal = '"arn:aws:iam::123456789012:root"'
        varb = ""
    elif spec.mode == "variable":
        principal = "var.principal"
        varb = '''
variable "principal" {
  type    = string
  default = "*"
}
'''
    else:
        principal = '"*"'
        varb = ""
    body = f'''
resource "aws_ecr_repository" "this" {{
  name                 = "eval-{spec.module_id}"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration {{
    scan_on_push = true
  }}
  encryption_configuration {{
    encryption_type = "AES256"
  }}
}}

resource "aws_ecr_repository_policy" "this" {{
  repository = aws_ecr_repository.this.name
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect    = "Allow"
      Principal = {principal}
      Action    = ["ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage"]
    }}]
  }})
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_snapshot_public(spec) -> str:
    if spec.label == "secure":
        group, varb = '"self"', ""
        # launch permission omitted / restricted to a specific account
        perm = '''
resource "aws_snapshot_create_volume_permission" "this" {
  snapshot_id = aws_ebs_snapshot.this.id
  account_id  = "123456789012"
}
'''
    elif spec.mode == "variable":
        perm = '''
resource "aws_ami_launch_permission" "this" {
  image_id = aws_ami.this.id
  group    = var.launch_group
}

variable "launch_group" {
  type    = string
  default = "all"
}
'''
        varb = ""
    else:
        perm = '''
resource "aws_ami_launch_permission" "this" {
  image_id = aws_ami.this.id
  group    = "all"
}
'''
        varb = ""
    body = f'''
resource "aws_ebs_volume" "this" {{
  availability_zone = "{spec.region}a"
  size              = 10
  encrypted         = true
}}

resource "aws_ebs_snapshot" "this" {{
  volume_id   = aws_ebs_volume.this.id
  description = "eval snapshot {spec.module_id}"
}}

resource "aws_ami" "this" {{
  name                = "eval-{spec.module_id}"
  virtualization_type = "hvm"
  root_device_name    = "/dev/xvda"
  ebs_block_device {{
    device_name = "/dev/xvda"
    snapshot_id = aws_ebs_snapshot.this.id
  }}
}}

{perm}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_instance_public_ip(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=False,
        insecure=True,
        insecure_alt=True,
        var_name="associate_public_ip",
    )
    body = f'''
resource "aws_instance" "this" {{
  ami                         = "ami-0c1c8c9e0eval0001"
  instance_type               = "t3.micro"
  subnet_id                   = "subnet-0eval{spec.variant_id}"
  vpc_security_group_ids      = ["sg-0eval{spec.variant_id}"]
  associate_public_ip_address = {flag}
  monitoring                  = true
  metadata_options {{
    http_tokens = "required"
  }}
  root_block_device {{
    encrypted = true
  }}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_opensearch_public(spec) -> str:
    # Insecure: public endpoint with open access policy. Secure: VPC-only.
    if spec.label == "secure":
        vpc = '''
  vpc_options {
    subnet_ids         = ["subnet-0evala", "subnet-0evalb"]
    security_group_ids = ["sg-0evalos"]
  }
'''
        policy_principal = '"arn:aws:iam::123456789012:root"'
        varb = ""
    elif spec.mode == "variable":
        vpc = ""
        policy_principal = "var.principal"
        varb = '''
variable "principal" {
  type    = string
  default = "*"
}
'''
    else:
        vpc = ""
        policy_principal = '"*"'
        varb = ""
    body = f'''
resource "aws_opensearch_domain" "this" {{
  domain_name    = "eval-{spec.module_id.replace("_", "-")[:28]}"
  engine_version = "OpenSearch_2.11"
{vpc}
  encrypt_at_rest {{
    enabled = true
  }}
  node_to_node_encryption {{
    enabled = true
  }}
  ebs_options {{
    ebs_enabled = true
    volume_size = 10
  }}
  cluster_config {{
    instance_type = "t3.small.search"
  }}
  access_policies = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect    = "Allow"
      Principal = {policy_principal}
      Action    = "es:*"
      Resource  = "*"
    }}]
  }})
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def ps_neptune_public(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=False,
        insecure=True,
        insecure_alt=True,
        var_name="publicly_accessible",
    )
    body = f'''
resource "aws_neptune_cluster" "this" {{
  cluster_identifier                   = "eval-{spec.module_id}"
  engine                               = "neptune"
  backup_retention_period              = 7
  skip_final_snapshot                  = true
  storage_encrypted                    = true
  iam_database_authentication_enabled  = true
}}

resource "aws_neptune_cluster_instance" "this" {{
  identifier          = "eval-{spec.module_id}-i"
  cluster_identifier  = aws_neptune_cluster.this.id
  instance_class      = "db.t3.medium"
  publicly_accessible = {flag}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


PATTERNS = [
    ("ps-s3-acl", "S3 bucket ACL public", "HIGH", "aws_s3_bucket_acl.acl", ps_s3_acl),
    ("ps-s3-pab", "S3 public access block disabled", "HIGH", "aws_s3_bucket_public_access_block", ps_s3_public_access_block),
    ("ps-s3-policy", "S3 bucket policy Principal *", "HIGH", "aws_s3_bucket_policy.Principal", ps_s3_bucket_policy),
    ("ps-rds-public", "RDS instance publicly_accessible", "HIGH", "aws_db_instance.publicly_accessible", ps_rds_public),
    ("ps-redshift-public", "Redshift publicly_accessible", "HIGH", "aws_redshift_cluster.publicly_accessible", ps_redshift_public),
    ("ps-sqs-policy", "SQS queue policy Principal *", "HIGH", "aws_sqs_queue_policy.Principal", ps_sqs_policy),
    ("ps-sns-policy", "SNS topic policy Principal *", "HIGH", "aws_sns_topic_policy.Principal", ps_sns_policy),
    ("ps-ecr-policy", "ECR repository policy Principal *", "HIGH", "aws_ecr_repository_policy.Principal", ps_ecr_policy),
    ("ps-ami-public", "AMI launch permission group all", "HIGH", "aws_ami_launch_permission.group", ps_snapshot_public),
    ("ps-ec2-public-ip", "EC2 associate_public_ip_address", "MEDIUM", "aws_instance.associate_public_ip_address", ps_instance_public_ip),
    ("ps-opensearch-public", "OpenSearch public policy Principal *", "HIGH", "aws_opensearch_domain.access_policies", ps_opensearch_public),
    ("ps-neptune-public", "Neptune instance publicly_accessible", "HIGH", "aws_neptune_cluster_instance.publicly_accessible", ps_neptune_public),
]
