package terraform.weak_logging

import data.terraform.helpers as h
import rego.v1

deny contains msg if {
	h.has_resource("aws_s3_bucket")
	not h.has_resource("aws_s3_bucket_logging")
	not h.has_resource("aws_cloudtrail")
	not h.has_resource("aws_lb")
	not h.has_resource("aws_elb")
	msg := "weak_logging: S3 bucket without aws_s3_bucket_logging"
}

deny contains msg if {
	some name
	trail := input.resource.aws_cloudtrail[name]
	flag := object.get(trail, "enable_log_file_validation", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("weak_logging: aws_cloudtrail[%s] log-file validation disabled", [name])
}

deny contains msg if {
	h.has_resource("aws_vpc")
	not h.has_resource("aws_flow_log")
	msg := "weak_logging: VPC without aws_flow_log"
}

deny contains msg if {
	some name
	lb := input.resource.aws_lb[name]
	logs := object.get(lb, "access_logs", {})
	flag := object.get(logs, "enabled", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("weak_logging: aws_lb[%s] access_logs disabled", [name])
}

deny contains msg if {
	some name
	elb := input.resource.aws_elb[name]
	logs := object.get(elb, "access_logs", {})
	flag := object.get(logs, "enabled", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("weak_logging: aws_elb[%s] access_logs disabled", [name])
}

deny contains msg if {
	some name
	db := input.resource.aws_db_instance[name]
	exports := object.get(db, "enabled_cloudwatch_logs_exports", [])
	not h.is_var_ref(exports)
	h.is_empty_list(exports)
	msg := sprintf("weak_logging: aws_db_instance[%s] empty CloudWatch log exports", [name])
}

deny contains msg if {
	h.has_resource("aws_api_gateway_stage")
	not h.has_resource("aws_api_gateway_method_settings")
	msg := "weak_logging: API Gateway stage without method settings / execution logs"
}

deny contains msg if {
	some name
	eks := input.resource.aws_eks_cluster[name]
	types := object.get(eks, "enabled_cluster_log_types", [])
	not h.is_var_ref(types)
	h.is_empty_list(types)
	msg := sprintf("weak_logging: aws_eks_cluster[%s] empty control-plane logs", [name])
}

deny contains msg if {
	some name
	rs := input.resource.aws_redshift_cluster[name]
	logging := object.get(rs, "logging", {})
	flag := object.get(logging, "enable", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("weak_logging: aws_redshift_cluster[%s] audit logging disabled", [name])
}

deny contains msg if {
	some name
	msk := input.resource.aws_msk_cluster[name]
	walk(msk, [p, v])
	p[count(p) - 1] == "enabled"
	v == false
	msg := sprintf("weak_logging: aws_msk_cluster[%s] broker logging disabled", [name])
}

deny contains msg if {
	h.has_resource("aws_wafv2_web_acl")
	not h.has_resource("aws_wafv2_web_acl_logging_configuration")
	msg := "weak_logging: WAFv2 ACL without logging configuration"
}
