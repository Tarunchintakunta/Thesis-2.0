# Ethics and acceptable-use checklist

A checklist to go through **before** the pilot. The NCI ethics declaration
itself is the student's own form to complete and sign - this file only lists
the facts it should rest on.

## Scope

- [ ] No human participants, no personal data, no survey or interview
- [ ] Payloads are synthetic (`src/driver/schedule.py`, `data/payload_template.json`): made-up account ids and amounts from a seeded random generator
- [ ] The target system is the operator's own AWS account and only resources created for this study (`infra/`, tagged `project = lambda-idempotency-eval`)
- [ ] No third-party systems are tested, scanned or loaded

## Acceptable use

- [ ] Failures are injected **inside** the function (sleep past its own timeout); no overload of AWS services
- [ ] Concurrency is bounded (`--workers`, default 1; the campaign plan uses 16)
- [ ] Hard stop in the driver: `budget.max_invocations` in `config/experiment.yaml` (warm-up calls count)
- [ ] CloudWatch alarms on daily invocations and write units; monthly budget e-mail when `alert_email` is set
- [ ] Failed conditional checks are reported as cost (they are billed)

## Before / after the runs

- [ ] AWS credentials are never committed (`.gitignore`, no keys in configs)
- [ ] `terraform destroy` after the last run, and the console checked for leftovers (log group, alarms, budget)
- [ ] Raw run folders contain only synthetic data and can be published with the artefact

Vikas Reddy Amanagantti
