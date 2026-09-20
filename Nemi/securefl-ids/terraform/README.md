# Terraform — securefl-ids

Portable research IaC for the **SecureFL-IDS cloud-native FL+DP** AWS evaluation surface.

## Policy
- Tags use `project` / `managed_by` / `purpose` / `data` only.
- **No student name or student ID** in `.tf`, `.tfvars`, or default tags.
- Free Tier: default `t3.micro`, destroy-after-round.
- **No Lambda** (shared-account `ConcurrentExecutions=10` is held by other campaigns).

## Lite live round
```bash
cd Nemi/securefl-ids
make live-cloud-fl
```

This applies 1× `t3.micro` (AL2023) + S3 artefacts + CloudWatch logs, runs 2-client × 3-round FL on the instance (S3 round-trip of global weights), copies `results/live/cloud_lite_summary.json`, then `terraform destroy`.

Default `client_count=0`: federated clients are in-process on the server node. Extra client EC2 nodes are optional beyond-CA2.

## Manual
```bash
cd Nemi/securefl-ids/terraform
terraform init
terraform plan
terraform apply
# after campaigns:
terraform destroy
```

Default region: `eu-west-1`. AMI defaults to latest AL2023 x86_64 via SSM. Docker/K8s overlays are beyond-CA2.
