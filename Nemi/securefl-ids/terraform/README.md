# Terraform — securefl-ids

Portable research IaC for the **SecureFL-IDS cloud-native FL+DP** AWS evaluation surface.

## Policy
- Tags use `project` / `managed_by` / `purpose` / `data` only.
- **No student name or student ID** in `.tf`, `.tfvars`, or default tags.
- Apply only when the alignment-first gate allows live AWS for this thesis.

## Usage
```bash
cd Nemi/securefl-ids/terraform
terraform init
terraform plan
terraform apply
# after campaigns:
terraform destroy
```

Default region: `eu-west-1` (override with `-var=region=...`).

Pass `-var=ami_id=ami-...` to create server/client EC2 nodes. Docker/K8s overlays are optional future work.
