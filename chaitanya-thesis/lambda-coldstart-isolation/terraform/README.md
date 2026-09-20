# Terraform — lambda-coldstart-isolation

Portable research IaC for the **Lambda Init Duration isolation** AWS evaluation surface.

## Policy
- Tags use `project` / `managed_by` / `purpose` / `data` only.
- **No student name or student ID** in `.tf`, `.tfvars`, or default tags.
- Apply only when the alignment-first gate allows live AWS for this thesis.

## Usage
```bash
cd chaitanya-thesis/lambda-coldstart-isolation/terraform
terraform init
terraform plan
terraform apply
# after campaigns:
terraform destroy
```

Default region: `eu-west-1` (override with `-var=region=...`).

Build `../build/python-default.zip` before `apply` if creating the function. Multi-runtime cells can remain in SAM once stripped of identifiers.
