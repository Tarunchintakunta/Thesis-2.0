# Ethics and budget notes

Kondragunta Lakshmi Chaitanya - 25171216

These are working notes for the artefact. The Declaration of Ethics
Consideration itself has to be filed by the student on Moodle - nothing in this
repository replaces it.

## Scenario

* **No human participants.** Nobody is surveyed, observed or recruited.
* **No personal or secondary data.** The only input is `payloads/fixed_payload.json`
  (a seed string and 20 small integers). Logs contain request ids, durations and
  memory numbers - no user data.
* **Target system: the student's own AWS account** (self-owned target). The
  deploy script prints the account id before deploying so it is obvious which
  account is used. No other organisation's system is touched.

## Cost and fair use

* Daily cap: `budget.daily_usd` in `configs/experiment.yaml` ($2.00). The
  invokers check it before every call and stop the run if the next call could
  pass it (`src/coldstart/budget.py`). Every call is written to `data/spend_log.csv`.
* Up-front estimate: `python scripts/budget_guard.py --plan configs/experiment.yaml`
  (free tier ignored, so the real bill should be lower).
* Burst concurrency is 20, far below the default account concurrency limit.
  The study does not try to stress shared multi-tenant capacity.
* The warmer runs every 5 minutes and only during the warming phase (the rule is
  created disabled). Provisioned concurrency is not used.
* `scripts/teardown.sh` removes the stack (and the warmer rule) when the campaign
  is finished. Log retention is 7 days.

## Energy and resources

Each cold sample is one short invocation. The whole planned campaign is a few
thousand invocations of a ~20 ms workload. The local proxy benchmark runs once
on a GitHub Actions runner (a few minutes of CI time).

## Responsible disclosure

If the study finds platform behaviour that looks like a bug or a security issue
(not just "slow"), it is reported to AWS through their vulnerability reporting
page before being written up in detail.

## Honesty rules the code enforces

* `DATA_MODE=mock` data is synthetic. Every mock row has `data_mode = mock`,
  every mock figure has a SYNTHETIC watermark and the analysis refuses to mix
  mock and live rows.
* The local benchmark is always called an "init proxy", never an Init Duration.
* If the live campaign is incomplete, results are labelled preliminary/pilot and
  no significance claims are made from mock or proxy data about AWS Lambda.
