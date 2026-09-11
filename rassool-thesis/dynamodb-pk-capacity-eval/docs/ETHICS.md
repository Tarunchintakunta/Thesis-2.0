# Ethics and budget notes

Rasool Basha Durbesula - 24205478

Working notes for the artefact; the Moodle ethics declaration is filed by the student.

* **No participants, no personal data.** Every item is a synthetic order made by
  `workloads/generator/keys.py` (ids like `o0001234`, `c00042`, a padding string).
* **Own account only.** All load originates from, and targets, the student's own
  AWS account. Nothing touches other tenants' resources.
* **Acceptable use.** 200 ops/s sustained, 1,000 ops/s in 30-second bursts, far
  below account limits. The throttle-storm alarms and the abort rule (3 batches in
  a row above 50% throttled) stop a cell that goes wrong.
* **Budget.** Estimated before running (`RUNBOOK.md`); daily cap in
  `config/experiment.yaml` checked by `run_matrix.py`; optional AWS Budgets email
  alert from Terraform. The campaign is not free-tier-safe - see ASSUMPTIONS C3.
  `terraform destroy` straight after the campaign stops all charges.
* **Energy.** Run counts come from the pre-set design (n = 30), not from "as much
  as the budget allows".
* **Reporting integrity.** Analysis plan and cost derivation are fixed before data;
  throttled and failed operations are published, never dropped; every figure
  carries the single-account, single-region scope.
* **Disclosure.** Undocumented service behaviour, if found, goes to AWS first.
* **Release.** IaC, workload code and the collected measurements are released so
  every figure can be recomputed.
