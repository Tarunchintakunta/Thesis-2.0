"""Shared HCL helpers for the labelled Terraform corpus generator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

EVAL_BANNER = """# EVALUATION ONLY — do not terraform apply.
# Synthetic labelled AWS Terraform module for scanner and policy-as-code measurement.
# Category: {category} | Label: {label} | Module: {module_id} | Pattern: {pattern_id}
"""

CATEGORIES = (
    "public_storage",
    "overpermissive_access",
    "encryption_at_rest",
    "weak_logging",
)

CATEGORY_PREFIX = {
    "public_storage": "ps",
    "overpermissive_access": "oa",
    "encryption_at_rest": "enc",
    "weak_logging": "log",
}

REGIONS = (
    "eu-west-1",
    "eu-west-2",
    "us-east-1",
    "eu-central-1",
    "ap-southeast-1",
)

# Formal N: 60 modules / category × 4 categories = 240.
# 12 patterns × (2 secure + 3 insecure) = 60; 36/60 = 60% defective.
VARIANTS = (
    ("s01", "secure", "direct"),
    ("s02", "secure", "direct_alt"),
    ("i01", "insecure", "direct"),
    ("i02", "insecure", "variable"),
    ("i03", "insecure", "alternate"),
)


@dataclass(frozen=True)
class ModuleSpec:
    module_id: str
    category: str
    pattern_id: str
    pattern_title: str
    variant_id: str
    label: str  # secure | insecure
    mode: str
    region: str
    severity: str
    defect_attribute: str
    sibling_id: str
    description: str


def tf_preamble(region: str) -> str:
    return f"""terraform {{
  required_version = ">= 1.5.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{region}"
}}
"""


def hcl_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return str(value)
    if isinstance(value, list):
        inner = ", ".join(hcl_value(v) for v in value)
        return f"[{inner}]"
    return json.dumps(value)


def lit_or_var(
    *,
    label: str,
    mode: str,
    secure: Any,
    insecure: Any,
    insecure_alt: Any,
    var_name: str,
) -> tuple[str, str]:
    """Return (HCL expression, optional variable block).

    Variable-indirection insecure variants put the defective value in the
    variable default so the resource attribute is `var.<name>` rather than a
    literal. That is the intended residual-risk / false-negative case for
    literal-matching policy gates.
    """
    if label == "secure":
        return hcl_value(secure), ""
    if mode == "variable":
        default = hcl_value(insecure)
        type_name = "bool" if isinstance(insecure, bool) else "string"
        if isinstance(insecure, list):
            type_name = "list(string)"
        block = f'''
variable "{var_name}" {{
  type    = {type_name}
  default = {default}
}}
'''
        return f"var.{var_name}", block
    chosen = insecure_alt if mode == "alternate" else insecure
    return hcl_value(chosen), ""


def compose(banner: str, preamble: str, variables: str, body: str) -> str:
    parts = [banner.rstrip(), preamble.rstrip()]
    extra = (variables or "").strip()
    if extra:
        parts.append(extra)
    parts.append(body.strip())
    return "\n\n".join(parts) + "\n"
