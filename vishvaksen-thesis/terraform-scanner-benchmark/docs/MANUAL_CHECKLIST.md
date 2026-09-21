# Manual checklist — human rater protocol

This is the formal “manual review” instrument for CA2 Objective 2.  
A human rater inspects **only** `main.tf` for one module, against that
module’s **labelled category**. Do not run scanners. Do not deploy.
Do not open `corpus/labels.csv` or sibling modules while scoring.

**Scripted pass:** `scripts/run_checklist.py` applies the same items as
regexes. That pass is **not** an independent human rater. Cite scripted
figures only as “scripted checklist”, never as human-review accuracy.

---

## Rater briefing (read once)

1. You receive: `module_id`, `category`, path to `main.tf`, and a blank
   scoring sheet (`docs/CHECKLIST_SCORING_SHEET.md`).
2. You do **not** receive: oracle `label`, `severity`, sibling secure
   module, scanner output, or other raters’ sheets.
3. Work category by category. Use only the item list for that category.
4. For each item: **Fail** if the condition is true on the HCL you see;
   **Pass** / N/A if not applicable or not true.
5. Module verdict: **Fail (insecure)** if **any** applicable item is Fail;
   else **Pass (secure)**.
6. Variable-only defects (`var.foo` with no literal insecure value in
   `main.tf`) are **Pass** under this instrument (same rule as the
   scripted pass). Note them under “notes” if you wish; do not Fail.
7. Record start/end time. One sheet per module. No terraform apply.

---

## Scoring rule (summary)

| Outcome | Rule |
|---------|------|
| Fail (insecure / positive) | ≥1 category checklist item is Fail |
| Pass (secure / negative) | All applicable items Pass / N/A |

---

## public_storage

1. S3 ACL is `public-read`, `public-read-write`, or `authenticated-read`.
2. S3 public access block flags are `false`.
3. Bucket/queue/topic/repo/OpenSearch policy `Principal` is `*`.
4. `publicly_accessible = true` on RDS / Redshift / Neptune.
5. `associate_public_ip_address = true` on EC2.
6. AMI launch permission `group = "all"`.

## overpermissive_access

1. Security-group or NACL ingress from `0.0.0.0/0` or `::/0`.
2. IAM `Action` and/or `Resource` is `*`, or `s3:*` on a user policy.
3. Managed policy `AdministratorAccess` or `IAMFullAccess`.
4. Lambda permission `principal = "*"`.
5. KMS / Secrets Manager policy principal `*`.
6. EKS `public_access_cidrs` includes `0.0.0.0/0`.

## encryption_at_rest

1. `encrypted` / `storage_encrypted` / `sqs_managed_sse_enabled` /
   `at_rest_encryption_enabled` is `false`.
2. S3 bucket has no `aws_s3_bucket_server_side_encryption_configuration`.
3. SNS / log group `kms_*` is `null` or empty.
4. DynamoDB `server_side_encryption.enabled = false`.
5. Glue `catalog_encryption_mode = "DISABLED"`.
6. Kinesis `encryption_type = "NONE"`.

## weak_logging

1. CloudTrail `enable_log_file_validation = false`, or no trail when the
   module is a trail-presence fixture.
2. VPC without `aws_flow_log`.
3. ALB/ELB `access_logs.enabled = false`.
4. RDS `enabled_cloudwatch_logs_exports = []`.
5. EKS `enabled_cluster_log_types = []`.
6. S3 without `aws_s3_bucket_logging` (unless the fixture is a trail/LB).
7. API Gateway stage without method settings.
8. WAF ACL without logging configuration.
9. Redshift `logging.enable = false` or MSK broker logs disabled.

---

## Deliverables after a human pass

- One filled sheet per module (or CSV export of the same fields).
- Batch log: rater ID, date, tool versions **not used**, module list.
- For the 20% dual-review subsample, follow
  `docs/SECOND_REVIEW_PROTOCOL.md` (independent second human).

## Honesty

- Sample sheets under `docs/CHECKLIST_SAMPLE_FILLED_NONINDEPENDENT.md`
  are filled by the **scripted** pass and labelled
  **NON-INDEPENDENT / same-author**. They are training/format artefacts
  only.
- Until a human rater completes sheets, formal “manual checklist review”
  remains **not run**.
