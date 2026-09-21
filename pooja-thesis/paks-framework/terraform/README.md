# PAKS live AWS stack (Free-Tier-safe)

**Project tag:** `paks-k8s-live`  
**Do not touch:** Venkat `project=distributed-matrix-scaling` EC2 instances.

## What this creates

| Resource | Purpose |
|----------|---------|
| 1× `t3.micro` EC2 (AL2023) | Single-node **k3s** (not EKS) |
| S3 bucket | Upload live TRACE metrics JSON |
| CloudWatch log group + PutMetricData IAM | Formal CW path |
| SSM instance profile | No SSH key; control plane via SSM |

Kube-apiserver is **not** opened publicly. Live scale uses `kubectl` on the node via SSM.

## Lifecycle

```bash
cd terraform
terraform init
terraform apply -auto-approve
# … run scripts/run_live_aws_k8s.py from framework root …
terraform destroy -auto-approve
```

Always destroy after the eval. Verify only `paks-k8s-live` resources are gone; leave Venkat stacks alone.
