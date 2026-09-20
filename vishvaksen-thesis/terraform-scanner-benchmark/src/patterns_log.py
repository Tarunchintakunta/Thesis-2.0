"""Weak / missing logging Terraform patterns."""

from __future__ import annotations

from .common import EVAL_BANNER, compose, lit_or_var, tf_preamble


def _banner(spec) -> str:
    return EVAL_BANNER.format(
        category=spec.category,
        label=spec.label,
        module_id=spec.module_id,
        pattern_id=spec.pattern_id,
    )


def log_s3_access(spec) -> str:
    if spec.label == "secure":
        logging = '''
resource "aws_s3_bucket_logging" "this" {
  bucket        = aws_s3_bucket.this.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access/"
}

resource "aws_s3_bucket" "logs" {
  bucket = "eval-tf-{mid}-logs"
}

resource "aws_s3_bucket_public_access_block" "logs" {{
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}
'''.replace("{mid}", spec.module_id)
        # fix the double-brace issue by not using that approach
        logging = f'''
resource "aws_s3_bucket_logging" "this" {{
  bucket        = aws_s3_bucket.this.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access/"
}}

resource "aws_s3_bucket" "logs" {{
  bucket = "eval-tf-{spec.module_id}-logs"
}}

resource "aws_s3_bucket_public_access_block" "logs" {{
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}
'''
        varb = ""
    else:
        logging = ""
        varb = '''
variable "enable_access_logging" {
  type    = bool
  default = false
}
''' if spec.mode == "variable" else ""
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

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {{
  bucket = aws_s3_bucket.this.id
  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "aws:kms"
    }}
  }}
}}

{logging}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_cloudtrail_validation(spec) -> str:
    flag, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="enable_log_file_validation",
    )
    body = f'''
resource "aws_cloudtrail" "this" {{
  name                          = "eval-{spec.module_id}"
  s3_bucket_name                = "eval-tf-{spec.module_id}-trail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = {flag}
  enable_logging                = true
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_vpc_flow(spec) -> str:
    if spec.label == "secure":
        flow = f'''
resource "aws_flow_log" "this" {{
  vpc_id               = aws_vpc.this.id
  traffic_type         = "ALL"
  log_destination_type = "cloud-watch-logs"
  log_destination      = aws_cloudwatch_log_group.flow.arn
  iam_role_arn         = "arn:aws:iam::123456789012:role/eval-flow"
}}

resource "aws_cloudwatch_log_group" "flow" {{
  name              = "/eval/{spec.module_id}/vpc-flow"
  retention_in_days = 90
}}
'''
        varb = ""
    else:
        flow = ""
        varb = '''
variable "enable_flow_logs" {
  type    = bool
  default = false
}
''' if spec.mode == "variable" else ""
    body = f'''
resource "aws_vpc" "this" {{
  cidr_block           = "10.20.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}}

{flow}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_alb_access(spec) -> str:
    enabled, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="access_logs_enabled",
    )
    body = f'''
resource "aws_lb" "this" {{
  name               = "eval-{spec.module_id}"[:32]
  internal           = true
  load_balancer_type = "application"
  subnets            = ["subnet-0evala", "subnet-0evalb"]
  security_groups    = ["sg-0evallb"]

  access_logs {{
    bucket  = "eval-tf-{spec.module_id}-alblogs"
    enabled = {enabled}
  }}
  drop_invalid_header_fields = true
}}
'''
    # Terraform doesn't support [:32] slice on a string like that - fix name length
    name = spec.module_id[:28]
    body = f'''
resource "aws_lb" "this" {{
  name               = "eval-{name}"
  internal           = true
  load_balancer_type = "application"
  subnets            = ["subnet-0evala", "subnet-0evalb"]
  security_groups    = ["sg-0evallb"]

  access_logs {{
    bucket  = "eval-tf-{spec.module_id}-alblogs"
    enabled = {enabled}
  }}
  drop_invalid_header_fields = true
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_rds_cw(spec) -> str:
    if spec.label == "secure":
        exports = '["postgresql", "upgrade"]'
        varb = ""
    elif spec.mode == "variable":
        exports = "var.log_exports"
        varb = '''
variable "log_exports" {
  type    = list(string)
  default = []
}
'''
    else:
        exports = "[]"
        varb = ""
    body = f'''
resource "aws_db_instance" "this" {{
  identifier                     = "eval-{spec.module_id}"
  engine                         = "postgres"
  engine_version                 = "15"
  instance_class                 = "db.t3.micro"
  allocated_storage              = 20
  username                       = "evaladmin"
  manage_master_user_password    = true
  skip_final_snapshot            = true
  backup_retention_period        = 7
  storage_encrypted              = true
  publicly_accessible            = false
  enabled_cloudwatch_logs_exports = {exports}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_apigw(spec) -> str:
    if spec.label == "secure":
        logs = f'''
resource "aws_api_gateway_method_settings" "this" {{
  rest_api_id = aws_api_gateway_rest_api.this.id
  stage_name  = aws_api_gateway_stage.this.stage_name
  method_path = "*/*"
  settings {{
    logging_level      = "INFO"
    data_trace_enabled = false
    metrics_enabled    = true
  }}
}}

resource "aws_cloudwatch_log_group" "api" {{
  name              = "API-Gateway-Execution-Logs_${{aws_api_gateway_rest_api.this.id}}/prod"
  retention_in_days = 90
}}
'''
        xray = "true"
        varb = ""
    elif spec.mode == "variable":
        logs = ""
        xray = "var.xray_tracing_enabled"
        varb = '''
variable "xray_tracing_enabled" {
  type    = bool
  default = false
}
'''
    else:
        logs = ""
        xray = "false"
        varb = ""
    body = f'''
resource "aws_api_gateway_rest_api" "this" {{
  name = "eval-{spec.module_id}"
}}

resource "aws_api_gateway_deployment" "this" {{
  rest_api_id = aws_api_gateway_rest_api.this.id
}}

resource "aws_api_gateway_stage" "this" {{
  rest_api_id           = aws_api_gateway_rest_api.this.id
  deployment_id         = aws_api_gateway_deployment.this.id
  stage_name            = "prod"
  xray_tracing_enabled  = {xray}
}}

{logs}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_eks(spec) -> str:
    if spec.label == "secure":
        types = '["api", "audit", "authenticator", "controllerManager", "scheduler"]'
        varb = ""
    elif spec.mode == "variable":
        types = "var.enabled_cluster_log_types"
        varb = '''
variable "enabled_cluster_log_types" {
  type    = list(string)
  default = []
}
'''
    else:
        types = "[]"
        varb = ""
    body = f'''
resource "aws_eks_cluster" "this" {{
  name     = "eval-{spec.module_id}"
  role_arn = "arn:aws:iam::123456789012:role/eval-eks"
  vpc_config {{
    subnet_ids             = ["subnet-0evala", "subnet-0evalb"]
    endpoint_public_access = false
  }}
  enabled_cluster_log_types = {types}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_cloudtrail_present(spec) -> str:
    if spec.label == "secure":
        trail = f'''
resource "aws_cloudtrail" "this" {{
  name                          = "eval-{spec.module_id}"
  s3_bucket_name                = "eval-tf-{spec.module_id}-trail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  enable_logging                = true
}}
'''
        varb = ""
    else:
        trail = ""
        varb = '''
variable "enable_cloudtrail" {
  type    = bool
  default = false
}
''' if spec.mode == "variable" else ""
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

{trail}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_redshift_audit(spec) -> str:
    enabled, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="audit_logging",
    )
    body = f'''
resource "aws_redshift_cluster" "this" {{
  cluster_identifier  = "eval-{spec.module_id}"
  node_type           = "dc2.large"
  master_username     = "evaladmin"
  master_password     = var.master_password
  cluster_type        = "single-node"
  publicly_accessible = false
  encrypted           = true
  skip_final_snapshot = true
  logging {{
    enable        = {enabled}
    bucket_name   = "eval-tf-{spec.module_id}-rslogs"
    s3_key_prefix = "redshift/"
  }}
}}

variable "master_password" {{
  type      = string
  sensitive = true
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_msk(spec) -> str:
    if spec.label == "secure":
        logging = '''
  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = "/eval/msk"
      }
    }
  }
'''
        varb = ""
    elif spec.mode == "variable":
        logging = '''
  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = var.broker_logs
        log_group = "/eval/msk"
      }
    }
  }
'''
        varb = '''
variable "broker_logs" {
  type    = bool
  default = false
}
'''
    else:
        logging = '''
  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled = false
      }
    }
  }
'''
        varb = ""
    body = f'''
resource "aws_msk_cluster" "this" {{
  cluster_name           = "eval-{spec.module_id}"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3
  broker_node_group_info {{
    instance_type   = "kafka.t3.small"
    client_subnets  = ["subnet-0evala", "subnet-0evalb", "subnet-0evalc"]
    security_groups = ["sg-0evalmsk"]
  }}
  encryption_info {{
    encryption_in_transit {{
      client_broker = "TLS"
      in_cluster    = true
    }}
  }}
{logging}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_waf(spec) -> str:
    if spec.label == "secure":
        logging = f'''
resource "aws_wafv2_web_acl_logging_configuration" "this" {{
  resource_arn            = aws_wafv2_web_acl.this.arn
  log_destination_configs = ["arn:aws:logs:{spec.region}:123456789012:log-group:aws-waf-logs-eval"]
}}
'''
        varb = ""
    else:
        logging = ""
        varb = '''
variable "enable_waf_logging" {
  type    = bool
  default = false
}
''' if spec.mode == "variable" else ""
    body = f'''
resource "aws_wafv2_web_acl" "this" {{
  name  = "eval-{spec.module_id}"
  scope = "REGIONAL"
  default_action {{
    allow {{}}
  }}
  visibility_config {{
    cloudwatch_metrics_enabled = true
    metric_name                = "eval{spec.variant_id}"
    sampled_requests_enabled   = true
  }}
}}

{logging}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def log_elb_access(spec) -> str:
    enabled, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=True,
        insecure=False,
        insecure_alt=False,
        var_name="access_logs_enabled",
    )
    name = spec.module_id[:24]
    body = f'''
resource "aws_elb" "this" {{
  name               = "eval-{name}"
  availability_zones = ["{spec.region}a", "{spec.region}b"]
  internal           = true
  listener {{
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }}
  access_logs {{
    bucket  = "eval-tf-{spec.module_id}-elblogs"
    enabled = {enabled}
  }}
  health_check {{
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:80/"
    interval            = 30
  }}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


PATTERNS = [
    ("log-s3-access", "S3 access logging missing", "MEDIUM", "aws_s3_bucket_logging", log_s3_access),
    ("log-cloudtrail-validation", "CloudTrail log-file validation disabled", "HIGH", "aws_cloudtrail.enable_log_file_validation", log_cloudtrail_validation),
    ("log-vpc-flow", "VPC flow logs missing", "MEDIUM", "aws_flow_log", log_vpc_flow),
    ("log-alb-access", "ALB access logs disabled", "MEDIUM", "aws_lb.access_logs.enabled", log_alb_access),
    ("log-rds-cw", "RDS CloudWatch log exports empty", "MEDIUM", "aws_db_instance.enabled_cloudwatch_logs_exports", log_rds_cw),
    ("log-apigw", "API Gateway stage without method logging", "MEDIUM", "aws_api_gateway_method_settings", log_apigw),
    ("log-eks-control", "EKS control-plane logs empty", "MEDIUM", "aws_eks_cluster.enabled_cluster_log_types", log_eks),
    ("log-cloudtrail-missing", "CloudTrail trail missing", "HIGH", "aws_cloudtrail", log_cloudtrail_present),
    ("log-redshift-audit", "Redshift audit logging disabled", "MEDIUM", "aws_redshift_cluster.logging.enable", log_redshift_audit),
    ("log-msk-broker", "MSK broker logs disabled", "MEDIUM", "aws_msk_cluster.logging_info", log_msk),
    ("log-waf", "WAFv2 logging configuration missing", "MEDIUM", "aws_wafv2_web_acl_logging_configuration", log_waf),
    ("log-elb-access", "Classic ELB access logs disabled", "MEDIUM", "aws_elb.access_logs.enabled", log_elb_access),
]
