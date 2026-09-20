# Terraform — lambda-idempotency-eval

Portable research IaC for the **Lambda+DynamoDB idempotency** AWS evaluation surface.

## Policy
- Tags use `project` / `managed_by` / `purpose` / `data` only.
- **No student name or student ID** in `.tf`, `.tfvars`, or default tags.
- Apply only when the alignment-first gate allows live AWS for this thesis.

## Usage
```bash
cd vikas-thesis/lambda-idempotency-eval/infra
terraform init
terraform plan
terraform apply
# after campaigns:
terraform destroy
```

Default region: `eu-west-1` (override with `-var=region=...`).

Existing module tree; student identifier tags removed.
