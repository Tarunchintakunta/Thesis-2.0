# Checklist sample sheets — NON-INDEPENDENT / same-author

**PASS TYPE: NON-INDEPENDENT / same-author (scripted checklist)**

These sheets are filled by `scripts/run_checklist.py` (regex procedure),
not by an independent human rater. They exist so a future human rater
can see the expected sheet format. **Do not cite as human-review evidence.**

Source: `results/checklist_verdicts.json` (scripted).

---

## Sample 1: `ps-001-ps-s3-acl-s01`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `ps-001-ps-s3-acl-s01` |
| category | `public_storage` |
| oracle label (hidden from human raters) | `secure` — shown here only for this sample artefact |
| Scripted predicted | `secure` |
| Module verdict | **Pass (secure)** |
| hits (regex / absence) | `[]` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | S3 ACL public-read / public-read-write / authenticated-read | X | | |  |
| 2 | S3 public access block flags false | X | | |  |
| 3 | Policy Principal * | X | | |  |
| 4 | publicly_accessible = true | X | | |  |
| 5 | associate_public_ip_address = true | X | | |  |
| 6 | AMI group = all | X | | |  |

---

## Sample 2: `ps-003-ps-s3-acl-i01`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `ps-003-ps-s3-acl-i01` |
| category | `public_storage` |
| oracle label (hidden from human raters) | `insecure` — shown here only for this sample artefact |
| Scripted predicted | `insecure` |
| Module verdict | **Fail (insecure)** |
| hits (regex / absence) | `['acl\\s*=\\s*"(public-read|public-read-write|authenticated-read)"', 'block_public_acls\\s*=\\s*false', 'restrict_public_buckets\\s*=\\s*false']` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | S3 ACL public-read / public-read-write / authenticated-read | | X | | scripted hit present |
| 2 | S3 public access block flags false | | | X | not separately ticked in sample |
| 3 | Policy Principal * | | | X | not separately ticked in sample |
| 4 | publicly_accessible = true | | | X | not separately ticked in sample |
| 5 | associate_public_ip_address = true | | | X | not separately ticked in sample |
| 6 | AMI group = all | | | X | not separately ticked in sample |

---

## Sample 3: `ps-009-ps-s3-pab-i02`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `ps-009-ps-s3-pab-i02` |
| category | `public_storage` |
| oracle label (hidden from human raters) | `insecure` — shown here only for this sample artefact |
| Scripted predicted | `secure` |
| Module verdict | **Pass (secure)** |
| hits (regex / absence) | `[]` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | S3 ACL public-read / public-read-write / authenticated-read | X | | | scripted FN (var.* / shape) |
| 2 | S3 public access block flags false | X | | |  |
| 3 | Policy Principal * | X | | |  |
| 4 | publicly_accessible = true | X | | |  |
| 5 | associate_public_ip_address = true | X | | |  |
| 6 | AMI group = all | X | | |  |

> Scripted **false negative** vs oracle: human rater following the
> same literal-only rule would also Pass; a stricter human might Fail.

---

## Sample 4: `oa-001-oa-sg-ssh-s01`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `oa-001-oa-sg-ssh-s01` |
| category | `overpermissive_access` |
| oracle label (hidden from human raters) | `secure` — shown here only for this sample artefact |
| Scripted predicted | `secure` |
| Module verdict | **Pass (secure)** |
| hits (regex / absence) | `[]` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | Ingress 0.0.0.0/0 or ::/0 | X | | |  |
| 2 | IAM Action/Resource * or s3:* | X | | |  |
| 3 | AdministratorAccess / IAMFullAccess | X | | |  |
| 4 | Lambda principal * | X | | |  |
| 5 | KMS/Secrets principal * | X | | |  |
| 6 | EKS public_access_cidrs 0.0.0.0/0 | X | | |  |

---

## Sample 5: `oa-003-oa-sg-ssh-i01`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `oa-003-oa-sg-ssh-i01` |
| category | `overpermissive_access` |
| oracle label (hidden from human raters) | `insecure` — shown here only for this sample artefact |
| Scripted predicted | `insecure` |
| Module verdict | **Fail (insecure)** |
| hits (regex / absence) | `['"0\\.0\\.0\\.0/0"']` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | Ingress 0.0.0.0/0 or ::/0 | | X | | scripted hit present |
| 2 | IAM Action/Resource * or s3:* | | | X | not separately ticked in sample |
| 3 | AdministratorAccess / IAMFullAccess | | | X | not separately ticked in sample |
| 4 | Lambda principal * | | | X | not separately ticked in sample |
| 5 | KMS/Secrets principal * | | | X | not separately ticked in sample |
| 6 | EKS public_access_cidrs 0.0.0.0/0 | | | X | not separately ticked in sample |

---

## Sample 6: `oa-019-oa-iam-star-i02`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `oa-019-oa-iam-star-i02` |
| category | `overpermissive_access` |
| oracle label (hidden from human raters) | `insecure` — shown here only for this sample artefact |
| Scripted predicted | `secure` |
| Module verdict | **Pass (secure)** |
| hits (regex / absence) | `[]` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | Ingress 0.0.0.0/0 or ::/0 | X | | | scripted FN (var.* / shape) |
| 2 | IAM Action/Resource * or s3:* | X | | |  |
| 3 | AdministratorAccess / IAMFullAccess | X | | |  |
| 4 | Lambda principal * | X | | |  |
| 5 | KMS/Secrets principal * | X | | |  |
| 6 | EKS public_access_cidrs 0.0.0.0/0 | X | | |  |

> Scripted **false negative** vs oracle: human rater following the
> same literal-only rule would also Pass; a stricter human might Fail.

---

## Sample 7: `enc-001-enc-s3-sse-s01`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `enc-001-enc-s3-sse-s01` |
| category | `encryption_at_rest` |
| oracle label (hidden from human raters) | `secure` — shown here only for this sample artefact |
| Scripted predicted | `secure` |
| Module verdict | **Pass (secure)** |
| hits (regex / absence) | `[]` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | encrypted / storage_encrypted / sse flags false | X | | |  |
| 2 | Missing S3 SSE configuration resource | X | | |  |
| 3 | kms_* null/empty | X | | |  |
| 4 | DynamoDB SSE enabled=false | X | | |  |
| 5 | Glue catalog_encryption_mode DISABLED | X | | |  |
| 6 | Kinesis encryption_type NONE | X | | |  |

---

## Sample 8: `enc-003-enc-s3-sse-i01`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `enc-003-enc-s3-sse-i01` |
| category | `encryption_at_rest` |
| oracle label (hidden from human raters) | `insecure` — shown here only for this sample artefact |
| Scripted predicted | `insecure` |
| Module verdict | **Fail (insecure)** |
| hits (regex / absence) | `['missing:aws_s3_bucket_server_side_encryption_configuration']` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | encrypted / storage_encrypted / sse flags false | | X | | scripted hit present |
| 2 | Missing S3 SSE configuration resource | | | X | not separately ticked in sample |
| 3 | kms_* null/empty | | | X | not separately ticked in sample |
| 4 | DynamoDB SSE enabled=false | | | X | not separately ticked in sample |
| 5 | Glue catalog_encryption_mode DISABLED | | | X | not separately ticked in sample |
| 6 | Kinesis encryption_type NONE | | | X | not separately ticked in sample |

---

## Sample 9: `enc-009-enc-ebs-i02`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `enc-009-enc-ebs-i02` |
| category | `encryption_at_rest` |
| oracle label (hidden from human raters) | `insecure` — shown here only for this sample artefact |
| Scripted predicted | `secure` |
| Module verdict | **Pass (secure)** |
| hits (regex / absence) | `[]` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | encrypted / storage_encrypted / sse flags false | X | | | scripted FN (var.* / shape) |
| 2 | Missing S3 SSE configuration resource | X | | |  |
| 3 | kms_* null/empty | X | | |  |
| 4 | DynamoDB SSE enabled=false | X | | |  |
| 5 | Glue catalog_encryption_mode DISABLED | X | | |  |
| 6 | Kinesis encryption_type NONE | X | | |  |

> Scripted **false negative** vs oracle: human rater following the
> same literal-only rule would also Pass; a stricter human might Fail.

---

## Sample 10: `log-001-log-s3-access-s01`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `log-001-log-s3-access-s01` |
| category | `weak_logging` |
| oracle label (hidden from human raters) | `secure` — shown here only for this sample artefact |
| Scripted predicted | `secure` |
| Module verdict | **Pass (secure)** |
| hits (regex / absence) | `[]` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | CloudTrail validation false / trail absence | X | | |  |
| 2 | VPC missing aws_flow_log | X | | |  |
| 3 | ALB/ELB access_logs.enabled false | X | | |  |
| 4 | RDS enabled_cloudwatch_logs_exports [] | X | | |  |
| 5 | EKS enabled_cluster_log_types [] | X | | |  |
| 6 | S3 missing aws_s3_bucket_logging | X | | |  |
| 7 | API GW stage missing method settings | X | | |  |
| 8 | WAF ACL missing logging config | X | | |  |
| 9 | Redshift/MSK logging disabled | X | | |  |

---

## Sample 11: `log-003-log-s3-access-i01`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `log-003-log-s3-access-i01` |
| category | `weak_logging` |
| oracle label (hidden from human raters) | `insecure` — shown here only for this sample artefact |
| Scripted predicted | `insecure` |
| Module verdict | **Fail (insecure)** |
| hits (regex / absence) | `['missing:aws_s3_bucket_logging']` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | CloudTrail validation false / trail absence | | X | | scripted hit present |
| 2 | VPC missing aws_flow_log | | | X | not separately ticked in sample |
| 3 | ALB/ELB access_logs.enabled false | | | X | not separately ticked in sample |
| 4 | RDS enabled_cloudwatch_logs_exports [] | | | X | not separately ticked in sample |
| 5 | EKS enabled_cluster_log_types [] | | | X | not separately ticked in sample |
| 6 | S3 missing aws_s3_bucket_logging | | | X | not separately ticked in sample |
| 7 | API GW stage missing method settings | | | X | not separately ticked in sample |
| 8 | WAF ACL missing logging config | | | X | not separately ticked in sample |
| 9 | Redshift/MSK logging disabled | | | X | not separately ticked in sample |

---

## Sample 12: `log-009-log-cloudtrail-validation-i02`

| Field | Value |
|-------|-------|
| **PASS TYPE** | **NON-INDEPENDENT / same-author (scripted)** |
| Rater ID | `scripted-checklist-v1` |
| module_id | `log-009-log-cloudtrail-validation-i02` |
| category | `weak_logging` |
| oracle label (hidden from human raters) | `insecure` — shown here only for this sample artefact |
| Scripted predicted | `secure` |
| Module verdict | **Pass (secure)** |
| hits (regex / absence) | `[]` |

| # | Item | Pass | Fail | N/A | Note |
|--:|------|:----:|:----:|:---:|------|
| 1 | CloudTrail validation false / trail absence | X | | | scripted FN (var.* / shape) |
| 2 | VPC missing aws_flow_log | X | | |  |
| 3 | ALB/ELB access_logs.enabled false | X | | |  |
| 4 | RDS enabled_cloudwatch_logs_exports [] | X | | |  |
| 5 | EKS enabled_cluster_log_types [] | X | | |  |
| 6 | S3 missing aws_s3_bucket_logging | X | | |  |
| 7 | API GW stage missing method settings | X | | |  |
| 8 | WAF ACL missing logging config | X | | |  |
| 9 | Redshift/MSK logging disabled | X | | |  |

> Scripted **false negative** vs oracle: human rater following the
> same literal-only rule would also Pass; a stricter human might Fail.

---

**Sheets in this sample:** 12 (≤3 per category: secure, TP, FN when present).

Independent human sheets: **NOT RUN**. Replace these with
`pass_type=independent_human` before claiming manual-review accuracy.
