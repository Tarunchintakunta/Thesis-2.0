package terraform.overpermissive_access

import data.terraform.helpers as h
import rego.v1

deny contains msg if {
	some name
	sg := input.resource.aws_security_group[name]
	some ingress in _ingress_blocks(sg)
	some cidr in _cidr_list(ingress)
	not h.is_var_ref(cidr)
	h.is_world_cidr(cidr)
	msg := sprintf("overpermissive_access: aws_security_group[%s] world CIDR %v", [name, cidr])
}

deny contains msg if {
	some name
	rule := input.resource.aws_network_acl_rule[name]
	cidr := object.get(rule, "cidr_block", "")
	not h.is_var_ref(cidr)
	h.is_world_cidr(cidr)
	object.get(rule, "rule_action", "") == "allow"
	msg := sprintf("overpermissive_access: aws_network_acl_rule[%s] allow from world", [name])
}

deny contains msg if {
	some name
	pol := input.resource.aws_iam_policy[name]
	walk(pol, [_, v])
	v == "*"
	msg := sprintf("overpermissive_access: aws_iam_policy[%s] contains *", [name])
}

deny contains msg if {
	some name
	pol := input.resource.aws_iam_user_policy[name]
	walk(pol, [_, v])
	v == "*"
	msg := sprintf("overpermissive_access: aws_iam_user_policy[%s] contains *", [name])
}

deny contains msg if {
	some name
	att := input.resource.aws_iam_role_policy_attachment[name]
	arn := object.get(att, "policy_arn", "")
	not h.is_var_ref(arn)
	endswith(arn, "AdministratorAccess")
	msg := sprintf("overpermissive_access: aws_iam_role_policy_attachment[%s] AdministratorAccess", [name])
}

deny contains msg if {
	some name
	att := input.resource.aws_iam_role_policy_attachment[name]
	arn := object.get(att, "policy_arn", "")
	not h.is_var_ref(arn)
	endswith(arn, "IAMFullAccess")
	msg := sprintf("overpermissive_access: aws_iam_role_policy_attachment[%s] IAMFullAccess", [name])
}

deny contains msg if {
	some name
	perm := input.resource.aws_lambda_permission[name]
	p := object.get(perm, "principal", "")
	not h.is_var_ref(p)
	p == "*"
	msg := sprintf("overpermissive_access: aws_lambda_permission[%s] principal=*", [name])
}

deny contains msg if {
	some name
	key := input.resource.aws_kms_key[name]
	walk(key, [_, v])
	v == "*"
	msg := sprintf("overpermissive_access: aws_kms_key[%s] policy contains *", [name])
}

deny contains msg if {
	some name
	sec := input.resource.aws_secretsmanager_secret_policy[name]
	walk(sec, [_, v])
	v == "*"
	msg := sprintf("overpermissive_access: aws_secretsmanager_secret_policy[%s] contains *", [name])
}

deny contains msg if {
	some name
	eks := input.resource.aws_eks_cluster[name]
	vpc := object.get(eks, "vpc_config", {})
	cidrs := _cidr_list(vpc)
	some cidr in cidrs
	not h.is_var_ref(cidr)
	h.is_world_cidr(cidr)
	msg := sprintf("overpermissive_access: aws_eks_cluster[%s] public_access_cidrs world", [name])
}

_ingress_blocks(sg) := blocks if {
	raw := object.get(sg, "ingress", [])
	is_array(raw)
	blocks := raw
}

_ingress_blocks(sg) := [raw] if {
	raw := object.get(sg, "ingress", null)
	is_object(raw)
}

_cidr_list(obj) := cidrs if {
	raw := object.get(obj, "cidr_blocks", [])
	is_array(raw)
	cidrs := raw
}

_cidr_list(obj) := object.get(obj, "public_access_cidrs", []) if {
	object.get(obj, "public_access_cidrs", null) != null
}

_cidr_list(obj) := [c] if {
	c := object.get(obj, "cidr_blocks", null)
	is_string(c)
}
