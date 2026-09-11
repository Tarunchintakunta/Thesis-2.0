# Analysis plan (fixed before the pilot)

Taken from the master prompt (sections 3 and 5) before any AWS data exists.
Changes after the pilot go in the **Amendments** table at the bottom with a
date and a reason; nothing above that table is edited once data has been seen.

## Design

- Write path: P1 plain put, P2 conditional put (`attribute_not_exists(pk)`), P3 idempotency key
- Retry multiplicity: 1, 2 or 5 deliveries of the same `request_id`
- Deliveries 1..N-1 time out **after** the write committed; delivery N succeeds,
  so a request has exactly N-1 injected retries
- All 9 cells are shuffled together with a fixed seed, so drift over the day
  affects every cell in the same way
- Constants: `config/versions.yaml` (region, runtime, memory, timeout, SDK, Terraform, provider)

## Metrics (per request, `analysis/metrics.py`)

| metric | definition | source |
|---|---|---|
| mutations | INSERT / MODIFY stream records of the business item `REQ#<id>` | DynamoDB stream (fallback: `business_writes` in the function records) |
| duplicate mutations | mutations - 1, not below 0 | |
| **duplicate-mutation rate** (primary) | sum of duplicate mutations / sum of injected retries, per cell | |
| conditional-check failures per retry | sum of `ccf` / sum of injected retries | function record |
| successful-retry rate | retries without a second mutation / injected retries | |
| capacity per request | sum of `ConsumedCapacity` over all deliveries, plus the documented write-unit rule for failed conditions whose error reports no capacity (kept in its own column) | `ReturnConsumedCapacity=TOTAL` |
| latency | driver round trip of the final (succeeding) delivery; in-function DynamoDB time as a secondary view | driver clock |

Multiplicity 1 has no retries, so it has no duplicate rate - it only gives latency and capacity.

## Hypotheses and tests

**Family D - duplicate mutation** (H0: equal rates; H1: guarded paths lower), at multiplicity 2 and 5:

- P1 vs P2 and P1 vs P3: two-proportion z-test, one-sided
- P2 vs P3: two-proportion z-test, two-sided (exploratory, kept inside the family so the correction stays conservative)
- 95 % CIs: Wilson per cell; a cluster bootstrap over requests as well, because the 4 retries of one request at multiplicity 5 are not independent; Newcombe's interval for differences
- chi-square on the cell x {duplicate, no duplicate} table, flagged when an expected count is below 5

**Family C - capacity per request** and **Family L - final-delivery latency** (H0: no difference; two-sided), P1-P2, P1-P3 and P2-P3 at multiplicity 1, 2 and 5:

- Shapiro-Wilk on both samples (at most 5000 random values each): both normal -> Welch's t-test (Cohen's d), otherwise Mann-Whitney U (rank-biserial correlation)
- 95 % bootstrap CI (B = 2000, seed 0) for the difference in means; mean and p95 per cell with bootstrap CIs

alpha = 0.05, Holm-Bonferroni within each family (D: 6 tests, C: 9, L: 9).

## Expectations and decision rules

| | expectation | rule |
|---|---|---|
| E1 | P1 duplicates on a majority of injected retries | at multiplicity 2 and 5: Wilson **and** cluster-bootstrap lower bounds > 0.5 |
| E2 | P2 and P3 cut the P1 rate by more than 90 % | at multiplicity 2 and 5: lower 95 % bound of 1 - p(guarded)/p(P1) > 0.90 (Katz log interval, 0.5 added to every cell when a count is 0) |
| E3 | P3 costs more capacity than P2 | at every multiplicity: bootstrap CI of mean(P3) - mean(P2) above 0 and Holm p < 0.05 |

"Inconclusive" means the point estimate meets the rule but the CI does not.

## Pilot rule (`analysis/pilot_size.py`)

Pilot: 50 requests per path at multiplicity 2. N is the largest of:

- duplicate rate: the smallest n whose Wilson interval at the pilot rate is at most +-1 percentage point
- capacity and latency: n = (1.96 x sd / (5 % of the mean))^2 with the pilot sd

If that is at most 1000, N = 1000 (the provisional value, supported by the pilot).
Otherwise N rises to the requirement, up to what the invocation budget allows
(`budget.max_invocations`), and the report says the CIs are wider than planned.
The script also prints a conservative N (pessimistic end of the pilot intervals)
for transparency only.

## Cold starts

Before each phase the driver sends warm-up waves (`warmup_rounds` x workers, not
analysed). Every record carries `cold_start`. A timeout resets the Lambda
execution environment, so the delivery after an injected timeout is often cold;
that is part of what a retry costs, so it is reported (share of cold final
deliveries, warm-only mean) and not removed.

## Sensitivity (outside the hypothesis families)

P3 at multiplicity 2 and 5 with the timeout **between** the business write and
marking the key COMPLETED (200 requests per cell). Reported descriptively.

## Data-quality rules

- a run folder is never reused; the schedule and ground truth are on disk before the first invoke
- missing deliveries, errors (other than the injected timeouts), lost log records and
  stream-vs-self-report disagreements are counted in `checks.csv` and reported - nothing is dropped silently
- if the stream could not be read within its 24-hour retention, the self-reported
  mutations are used and every table says so (`mutation_source`)

## Amendments

| date | change | reason |
|---|---|---|
| | | |

Vikas Reddy Amanagantti
