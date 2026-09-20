package terraform.public_storage

import data.terraform.helpers as h
import rego.v1

deny contains msg if {
	some name
	acl := input.resource.aws_s3_bucket_acl[name]
	val := object.get(acl, "acl", "")
	not h.is_var_ref(val)
	val in {"public-read", "public-read-write", "authenticated-read"}
	msg := sprintf("public_storage: aws_s3_bucket_acl[%s] acl=%v", [name, val])
}

deny contains msg if {
	some name
	pab := input.resource.aws_s3_bucket_public_access_block[name]
	flag := object.get(pab, "block_public_acls", true)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("public_storage: aws_s3_bucket_public_access_block[%s] block_public_acls is false", [name])
}

deny contains msg if {
	some name
	pab := input.resource.aws_s3_bucket_public_access_block[name]
	flag := object.get(pab, "restrict_public_buckets", true)
	not h.is_var_ref(flag)
	h.is_falsey(flag)
	msg := sprintf("public_storage: aws_s3_bucket_public_access_block[%s] restrict_public_buckets is false", [name])
}

deny contains msg if {
	some name
	db := input.resource.aws_db_instance[name]
	flag := object.get(db, "publicly_accessible", false)
	not h.is_var_ref(flag)
	flag == true
	msg := sprintf("public_storage: aws_db_instance[%s] publicly_accessible", [name])
}

deny contains msg if {
	some name
	rs := input.resource.aws_redshift_cluster[name]
	flag := object.get(rs, "publicly_accessible", false)
	not h.is_var_ref(flag)
	flag == true
	msg := sprintf("public_storage: aws_redshift_cluster[%s] publicly_accessible", [name])
}

deny contains msg if {
	some name
	inst := input.resource.aws_neptune_cluster_instance[name]
	flag := object.get(inst, "publicly_accessible", false)
	not h.is_var_ref(flag)
	flag == true
	msg := sprintf("public_storage: aws_neptune_cluster_instance[%s] publicly_accessible", [name])
}

deny contains msg if {
	some name
	ec2 := input.resource.aws_instance[name]
	flag := object.get(ec2, "associate_public_ip_address", false)
	not h.is_var_ref(flag)
	flag == true
	msg := sprintf("public_storage: aws_instance[%s] associate_public_ip_address", [name])
}

deny contains msg if {
	some name
	perm := input.resource.aws_ami_launch_permission[name]
	grp := object.get(perm, "group", "")
	not h.is_var_ref(grp)
	grp == "all"
	msg := sprintf("public_storage: aws_ami_launch_permission[%s] group=all", [name])
}

deny contains msg if {
	walk(input, [_, s])
	is_string(s)
	not h.is_var_ref(s)
	contains(s, "\"Principal\"")
	contains(s, "\"*\"")
	msg := "public_storage: policy document contains Principal *"
}

deny contains msg if {
	some name
	pol := input.resource.aws_s3_bucket_policy[name]
	walk(pol, [_, v])
	v == "*"
	msg := sprintf("public_storage: aws_s3_bucket_policy[%s] contains *", [name])
}

deny contains msg if {
	some name
	pol := input.resource.aws_sqs_queue_policy[name]
	walk(pol, [_, v])
	v == "*"
	msg := sprintf("public_storage: aws_sqs_queue_policy[%s] contains *", [name])
}

deny contains msg if {
	some name
	pol := input.resource.aws_sns_topic_policy[name]
	walk(pol, [_, v])
	v == "*"
	msg := sprintf("public_storage: aws_sns_topic_policy[%s] contains *", [name])
}

deny contains msg if {
	some name
	pol := input.resource.aws_ecr_repository_policy[name]
	walk(pol, [_, v])
	v == "*"
	msg := sprintf("public_storage: aws_ecr_repository_policy[%s] contains *", [name])
}

deny contains msg if {
	some name
	dom := input.resource.aws_opensearch_domain[name]
	not object.get(dom, "vpc_options", null)
	walk(object.get(dom, "access_policies", {}), [_, v])
	v == "*"
	msg := sprintf("public_storage: aws_opensearch_domain[%s] public * policy", [name])
}
