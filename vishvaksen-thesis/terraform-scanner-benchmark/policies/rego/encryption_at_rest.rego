package terraform.encryption_at_rest

import data.terraform.helpers as h
import rego.v1

deny contains msg if {
	h.has_resource("aws_s3_bucket")
	not h.has_resource("aws_s3_bucket_server_side_encryption_configuration")
	msg := "encryption_at_rest: S3 bucket without SSE configuration resource"
}

deny contains msg if {
	some name
	vol := input.resource.aws_ebs_volume[name]
	flag := object.get(vol, "encrypted", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("encryption_at_rest: aws_ebs_volume[%s] encrypted is false", [name])
}

deny contains msg if {
	some name
	db := input.resource.aws_db_instance[name]
	flag := object.get(db, "storage_encrypted", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("encryption_at_rest: aws_db_instance[%s] storage_encrypted is false", [name])
}

deny contains msg if {
	some name
	fs := input.resource.aws_efs_file_system[name]
	flag := object.get(fs, "encrypted", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("encryption_at_rest: aws_efs_file_system[%s] encrypted is false", [name])
}

deny contains msg if {
	some name
	topic := input.resource.aws_sns_topic[name]
	kms := object.get(topic, "kms_master_key_id", null)
	not h.is_var_ref(kms)
	h.is_falsey(kms)
	msg := sprintf("encryption_at_rest: aws_sns_topic[%s] missing kms_master_key_id", [name])
}

deny contains msg if {
	some name
	q := input.resource.aws_sqs_queue[name]
	flag := object.get(q, "sqs_managed_sse_enabled", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("encryption_at_rest: aws_sqs_queue[%s] SSE disabled", [name])
}

deny contains msg if {
	some name
	lg := input.resource.aws_cloudwatch_log_group[name]
	kms := object.get(lg, "kms_key_id", null)
	not h.is_var_ref(kms)
	h.is_falsey(kms)
	msg := sprintf("encryption_at_rest: aws_cloudwatch_log_group[%s] missing kms_key_id", [name])
}

deny contains msg if {
	some name
	tbl := input.resource.aws_dynamodb_table[name]
	sse := object.get(tbl, "server_side_encryption", {})
	flag := object.get(sse, "enabled", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("encryption_at_rest: aws_dynamodb_table[%s] SSE disabled", [name])
}

deny contains msg if {
	some name
	rs := input.resource.aws_redshift_cluster[name]
	flag := object.get(rs, "encrypted", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("encryption_at_rest: aws_redshift_cluster[%s] encrypted is false", [name])
}

deny contains msg if {
	some name
	rg := input.resource.aws_elasticache_replication_group[name]
	flag := object.get(rg, "at_rest_encryption_enabled", false)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("encryption_at_rest: aws_elasticache_replication_group[%s] at-rest encryption disabled", [name])
}

deny contains msg if {
	some name
	glue := input.resource.aws_glue_data_catalog_encryption_settings[name]
	walk(glue, [p, v])
	p[count(p) - 1] == "catalog_encryption_mode"
	v == "DISABLED"
	msg := sprintf("encryption_at_rest: aws_glue_data_catalog_encryption_settings[%s] DISABLED", [name])
}

deny contains msg if {
	some name
	ks := input.resource.aws_kinesis_stream[name]
	enc := object.get(ks, "encryption_type", "NONE")
	not h.is_var_ref(enc)
	enc == "NONE"
	msg := sprintf("encryption_at_rest: aws_kinesis_stream[%s] encryption_type NONE", [name])
}
