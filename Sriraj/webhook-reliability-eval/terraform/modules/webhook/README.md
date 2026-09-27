# Terraform module stub — webhook reliability

Resources sketched: SQS main + DLQ redrive (`maxReceiveCount=3`).

**Live phase (not floor):** add API Gateway (HMAC authorizer / Lambda authorizer),
processing Lambda, replay Lambda/scheduler, ElastiCache Redis, IAM, CloudWatch alarms.

Never place AWS keys or HMAC secrets in this tree. Use SSM/Secrets Manager names only.
