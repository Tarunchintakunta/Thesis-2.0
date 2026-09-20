"""Over-permissive identity / network access Terraform patterns."""

from __future__ import annotations

from .common import EVAL_BANNER, compose, lit_or_var, tf_preamble


def _banner(spec) -> str:
    return EVAL_BANNER.format(
        category=spec.category,
        label=spec.label,
        module_id=spec.module_id,
        pattern_id=spec.pattern_id,
    )


def _sg_ingress(spec, from_port: int, to_port: int, protocol: str, var_name: str) -> str:
    cidr, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure="10.0.0.0/16",
        insecure="0.0.0.0/0",
        insecure_alt="::/0",
        var_name=var_name,
    )
    proto = protocol if spec.mode != "alternate" or spec.label == "secure" else protocol
    body = f'''
resource "aws_security_group" "this" {{
  name        = "eval-{spec.module_id}"
  description = "Evaluation security group {spec.module_id}"
  vpc_id      = "vpc-0eval{spec.variant_id}"

  ingress {{
    description = "labelled ingress"
    from_port   = {from_port}
    to_port     = {to_port}
    protocol    = "{proto}"
    cidr_blocks = [{cidr}]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/8"]
  }}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def oa_sg_ssh(spec) -> str:
    return _sg_ingress(spec, 22, 22, "tcp", "ssh_cidr")


def oa_sg_all(spec) -> str:
    cidr, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure="10.0.0.0/16",
        insecure="0.0.0.0/0",
        insecure_alt="0.0.0.0/0",
        var_name="all_cidr",
    )
    proto = '"-1"' if spec.label == "insecure" else '"tcp"'
    from_p = 0 if spec.label == "insecure" else 443
    to_p = 0 if spec.label == "insecure" else 443
    if spec.mode == "alternate" and spec.label == "insecure":
        proto = '"-1"'
        from_p, to_p = 0, 65535
    body = f'''
resource "aws_security_group" "this" {{
  name        = "eval-{spec.module_id}"
  description = "Evaluation security group {spec.module_id}"
  vpc_id      = "vpc-0eval{spec.variant_id}"

  ingress {{
    description = "labelled ingress"
    from_port   = {from_p}
    to_port     = {to_p}
    protocol    = {proto}
    cidr_blocks = [{cidr}]
  }}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def oa_sg_rdp(spec) -> str:
    return _sg_ingress(spec, 3389, 3389, "tcp", "rdp_cidr")


def oa_iam_star(spec) -> str:
    if spec.label == "secure":
        action, resource = '"s3:GetObject"', '"arn:aws:s3:::eval-private/app/*"'
        varb = ""
    elif spec.mode == "variable":
        action, resource = "var.action", "var.resource"
        varb = '''
variable "action" {
  type    = string
  default = "*"
}

variable "resource" {
  type    = string
  default = "*"
}
'''
    elif spec.mode == "alternate":
        action, resource = '"*"', '"*"'
        varb = ""
    else:
        action, resource = '"*"', '"*"'
        varb = ""
    body = f'''
resource "aws_iam_policy" "this" {{
  name        = "eval-{spec.module_id}"
  description = "Evaluation IAM policy {spec.module_id}"
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect   = "Allow"
      Action   = {action}
      Resource = {resource}
    }}]
  }})
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def oa_iam_admin(spec) -> str:
    if spec.label == "secure":
        arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
        varb = ""
        attach = f'''
resource "aws_iam_role_policy_attachment" "this" {{
  role       = aws_iam_role.this.name
  policy_arn = "{arn}"
}}
'''
    elif spec.mode == "variable":
        varb = '''
variable "policy_arn" {
  type    = string
  default = "arn:aws:iam::aws:policy/AdministratorAccess"
}
'''
        attach = '''
resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = var.policy_arn
}
'''
    else:
        varb = ""
        arn = (
            "arn:aws:iam::aws:policy/IAMFullAccess"
            if spec.mode == "alternate"
            else "arn:aws:iam::aws:policy/AdministratorAccess"
        )
        attach = f'''
resource "aws_iam_role_policy_attachment" "this" {{
  role       = aws_iam_role.this.name
  policy_arn = "{arn}"
}}
'''
    body = f'''
resource "aws_iam_role" "this" {{
  name = "eval-{spec.module_id}"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect = "Allow"
      Principal = {{ Service = "ec2.amazonaws.com" }}
      Action = "sts:AssumeRole"
    }}]
  }})
}}

{attach}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def oa_nacl(spec) -> str:
    cidr, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure="10.0.0.0/16",
        insecure="0.0.0.0/0",
        insecure_alt="0.0.0.0/0",
        var_name="nacl_cidr",
    )
    proto = "-1" if spec.label == "insecure" else "6"
    from_p = 0 if spec.label == "insecure" else 443
    to_p = 0 if spec.label == "insecure" else 443
    body = f'''
resource "aws_network_acl" "this" {{
  vpc_id = "vpc-0eval{spec.variant_id}"
}}

resource "aws_network_acl_rule" "ingress" {{
  network_acl_id = aws_network_acl.this.id
  rule_number    = 100
  egress         = false
  protocol       = "{proto}"
  rule_action    = "allow"
  cidr_block     = {cidr}
  from_port      = {from_p}
  to_port        = {to_p}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def oa_lambda_permission(spec) -> str:
    principal, varb = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure="apigateway.amazonaws.com",
        insecure="*",
        insecure_alt="*",
        var_name="invoke_principal",
    )
    body = f'''
resource "aws_lambda_function" "this" {{
  function_name = "eval-{spec.module_id}"
  role          = "arn:aws:iam::123456789012:role/eval-lambda"
  handler       = "index.handler"
  runtime       = "python3.12"
  filename      = "placeholder.zip"
}}

resource "aws_lambda_permission" "this" {{
  statement_id  = "EvalInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = {principal}
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def oa_kms_policy(spec) -> str:
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
resource "aws_kms_key" "this" {{
  description             = "eval {spec.module_id}"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Sid       = "EvalKey"
      Effect    = "Allow"
      Principal = {{ AWS = {principal} }}
      Action    = "kms:*"
      Resource  = "*"
    }}]
  }})
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def oa_iam_s3_star(spec) -> str:
    action = '"s3:GetObject"' if spec.label == "secure" else '"s3:*"'
    if spec.mode == "variable" and spec.label == "insecure":
        action = "var.s3_actions"
        varb = '''
variable "s3_actions" {
  type    = string
  default = "s3:*"
}
'''
    elif spec.mode == "alternate" and spec.label == "insecure":
        action = '["s3:*", "s3-object-lambda:*"]'
        varb = ""
    else:
        varb = ""
    body = f'''
resource "aws_iam_user_policy" "this" {{
  name = "eval-{spec.module_id}"
  user = aws_iam_user.this.name
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect   = "Allow"
      Action   = {action}
      Resource = "arn:aws:s3:::eval-{spec.module_id}/*"
    }}]
  }})
}}

resource "aws_iam_user" "this" {{
  name = "eval-{spec.module_id}"
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


def oa_sg_postgres(spec) -> str:
    return _sg_ingress(spec, 5432, 5432, "tcp", "pg_cidr")


def oa_eks_public(spec) -> str:
    flag, varb1 = lit_or_var(
        label=spec.label,
        mode="direct" if spec.mode != "variable" else "variable",
        secure=False,
        insecure=True,
        insecure_alt=True,
        var_name="endpoint_public_access",
    )
    cidrs, varb2 = lit_or_var(
        label=spec.label,
        mode=spec.mode,
        secure=["10.0.0.0/16"],
        insecure=["0.0.0.0/0"],
        insecure_alt=["0.0.0.0/0"],
        var_name="public_access_cidrs",
    )
    # Secure: private endpoint. Insecure: public + world CIDR.
    body = f'''
resource "aws_eks_cluster" "this" {{
  name     = "eval-{spec.module_id}"
  role_arn = "arn:aws:iam::123456789012:role/eval-eks"
  vpc_config {{
    subnet_ids              = ["subnet-0evala", "subnet-0evalb"]
    endpoint_public_access  = {flag}
    endpoint_private_access = true
    public_access_cidrs     = {cidrs}
  }}
  enabled_cluster_log_types = ["api", "audit", "authenticator"]
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb1 + varb2, body)


def oa_secrets_policy(spec) -> str:
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
resource "aws_secretsmanager_secret" "this" {{
  name       = "eval-{spec.module_id}"
  kms_key_id = "alias/aws/secretsmanager"
}}

resource "aws_secretsmanager_secret_policy" "this" {{
  secret_arn = aws_secretsmanager_secret.this.arn
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect    = "Allow"
      Principal = {{ AWS = {principal} }}
      Action    = "secretsmanager:GetSecretValue"
      Resource  = "*"
    }}]
  }})
}}
'''
    return compose(_banner(spec), tf_preamble(spec.region), varb, body)


PATTERNS = [
    ("oa-sg-ssh", "Security group SSH from the world", "HIGH", "aws_security_group.ingress.cidr_blocks:22", oa_sg_ssh),
    ("oa-sg-all", "Security group all-traffic from the world", "HIGH", "aws_security_group.ingress.protocol:-1", oa_sg_all),
    ("oa-sg-rdp", "Security group RDP from the world", "HIGH", "aws_security_group.ingress.cidr_blocks:3389", oa_sg_rdp),
    ("oa-iam-star", "IAM policy Action * Resource *", "HIGH", "aws_iam_policy.Action/Resource", oa_iam_star),
    ("oa-iam-admin", "IAM AdministratorAccess attachment", "HIGH", "aws_iam_role_policy_attachment.policy_arn", oa_iam_admin),
    ("oa-nacl-all", "NACL allow-all ingress from the world", "HIGH", "aws_network_acl_rule.cidr_block", oa_nacl),
    ("oa-lambda-principal", "Lambda permission principal *", "HIGH", "aws_lambda_permission.principal", oa_lambda_permission),
    ("oa-kms-policy", "KMS key policy Principal *", "HIGH", "aws_kms_key.policy.Principal", oa_kms_policy),
    ("oa-iam-s3-star", "IAM user policy s3:*", "MEDIUM", "aws_iam_user_policy.Action", oa_iam_s3_star),
    ("oa-sg-postgres", "Security group PostgreSQL from the world", "HIGH", "aws_security_group.ingress.cidr_blocks:5432", oa_sg_postgres),
    ("oa-eks-public", "EKS public endpoint 0.0.0.0/0", "HIGH", "aws_eks_cluster.vpc_config.public_access_cidrs", oa_eks_public),
    ("oa-secrets-policy", "Secrets Manager policy Principal *", "HIGH", "aws_secretsmanager_secret_policy.Principal", oa_secrets_policy),
]
