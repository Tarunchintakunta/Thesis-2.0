# Data formats

## Run folder (`data/runs/<source>/<phase>/`, written by the driver)

| file | when | content |
|---|---|---|
| `schedule.csv` | before the first invoke | one row per planned delivery: `order, request_id, path, multiplicity, delivery, inject` |
| `ground_truth.jsonl` | before the first invoke | one line per request: `request_id, phase, path, multiplicity, inject_mode, injected_retries, intended_deliveries, order` |
| `deliveries.jsonl` | during the run | one line per delivery (below) |
| `run_info.json` | end of the run | phase, backend (`live` / `moto` / `local`), counts, workers, warm-up, start/end time, pinned versions |
| `stream.jsonl` | `python -m driver.streams` (within 24 h) | one line per stream record (below) |
| `cloudwatch.json` | `scripts/collect_cloudwatch.py` (optional) | CloudWatch sums over the run window next to the driver totals |

### `deliveries.jsonl`

| field | meaning |
|---|---|
| `request_id, phase, path, multiplicity, delivery, inject` | from the schedule |
| `status` | `ok`, `timeout` (injected), `error` (anything else) |
| `outcome` | `APPLIED`, `SUPPRESSED` (P2 condition failed), `REPLAYED` (P3 stored result), `REJECTED_IN_PROGRESS` (P3 live claim), `CRASH_BETWEEN` (P3 sensitivity) |
| `wcu, rcu` | capacity reported by DynamoDB for the delivery's calls |
| `wcu_ccf_rule` | write units of failed conditions that reported no capacity (documented rule) |
| `consumed_capacity` | `wcu + rcu` as logged by the function; empty = the record was lost |
| `ccf, calls, business_writes` | failed conditions, DynamoDB calls, writes of the business item |
| `latency_ms, ddb_ms` | handler time, time inside the DynamoDB calls |
| `rtt_ms` | driver round trip of the invoke |
| `cold_start` | first call in its execution environment |
| `exec_id` | Lambda request id of the delivery |
| `function_error, t_start` | Lambda error message (first 200 chars), driver clock at invoke |

### `stream.jsonl`

`event` (INSERT / MODIFY / REMOVE), `seq`, `pk`, `kind` (`business` or `idem_key`), `request_id`,
and the item version after and before the change: `exec_id, delivery, status` /
`old_exec_id, old_delivery, old_status`.

## Analysis output (`results/<source>/`)

| file | from | content |
|---|---|---|
| `pilot_sizing.csv`, `pilot_choice.json`, `pilot_report.md` | `analysis/pilot_size.py` | pilot estimates, required N, the decision |
| `requests.csv` | `analysis/analyse.py` | per-request metrics |
| `cells.csv` | | per path x multiplicity: duplicate rate with Wilson and cluster CIs, conditional failures, capacity and latency with bootstrap CIs, cold share, data checks |
| `dup_tests.csv`, `chi2.csv` | | family D tests with Holm |
| `capacity_tests.csv`, `latency_tests.csv` | | families C and L with Holm |
| `expectations.csv` | | E1-E3 decisions |
| `checks.csv` | | data-quality counts |
| `sensitivity_cells.csv`, `sensitivity_outcomes.csv` | | P3 crash-between-writes case |
| `summary.md` | | everything above in one file |

Figures go to `figures/<source>/`: `dup_rate.png`, `latency.png`, `capacity.png`, `surface.png`.
Only `live` is an AWS measurement; `moto` output is a functional check.

Vikas Reddy Amanagantti
