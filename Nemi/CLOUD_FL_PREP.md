# Cloud FL prep (Nemi) — do not apply

**Updated:** 2026-09-20  
**Why prep only:** Shared-account `ConcurrentExecutions=10`; Vikas campaign **r5 RUNNING**. Live FL apply is the sole AWS residual and is **deferred**.

## Local checks (no AWS mutations)

```bash
cd Nemi/securefl-ids/terraform
terraform fmt -check
terraform init -backend=false
terraform validate
```

`ami_id` default is empty → `aws_instance.server/client` **count = 0**. A future apply with the default would still create an S3 artifacts bucket, log group, and security group. **Do not apply** until concurrency is free **and** Free Tier / budget gate is explicit.

## When concurrency clears (Free Tier)

1. Confirm no other live Lambda/EC2 campaign is consuming the shared account.
2. `terraform plan` then `terraform apply` only with tags `project/managed_by/purpose/data` (already in `main.tf`; no student name/ID).
3. Run the FL campaign documented in `securefl-ids/README.md`.
4. `terraform destroy` the same day (destroy-after-round).

## Not done this pass

- No `terraform apply`
- No live accuracy/F1 cells
