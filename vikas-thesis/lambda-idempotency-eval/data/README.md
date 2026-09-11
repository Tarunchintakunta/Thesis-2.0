# data

Synthetic data only - no personal data anywhere in this project.

- `payload_template.json` - shape of the synthetic payment request the driver sends
- `runs/live/<phase>/` - raw live runs (schedule, ground truth, deliveries, stream); commit these after the campaign, they are the raw results
- `runs/moto/`, `runs/local/` - functional-check runs, recreated by `make functional`, not committed

File formats: `results/SCHEMA.md`.

Vikas Reddy Amanagantti
