# RUNBOOK — webhook-reliability-eval

## Local floor (required)

1. `cd Sriraj/webhook-reliability-eval`
2. `make setup && make test && make pilot`
3. Confirm `results/local_sim/pilot_results.json` exists and every cell has `"mode": "local_sim"`.
4. Do **not** quote these numbers as live AWS.

## Live AWS (optional later)

1. Create IAM user / profile in **student** account; export `AWS_PROFILE`.
2. Put HMAC secret in SSM/Secrets Manager — never in git.
3. Fill Lambda + API GW + ElastiCache into `terraform/modules/webhook`.
4. `terraform plan/apply` in `envs/dev`; run campaign; `terraform destroy`.
5. Tag resources `project=webhook-reliability-eval` only.

## Fault injection rates (CA2)

| Rate | Meaning |
|------|---------|
| 0% | Happy path (latency overhead RQ3) |
| 10% | Mild transient/permanent mix |
| 25% | Moderate |
| 50% | Stress (RQ1 success uplift) |

Duplicate injection default 10% for RQ2.

## Safety

- Synthetic data only.
- Destroy live stacks after runs.
- No force-push; no secret commits.
