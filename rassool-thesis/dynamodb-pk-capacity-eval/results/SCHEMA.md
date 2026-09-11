# results/ - schema only

Rasool Basha Durbesula - 24205478

Nothing in this folder is committed except this file: the numbers come from the
live campaign in the student's own AWS account (RUNBOOK.md) and no result is
made up in advance (master prompt 3.4).

## `batches.csv` - one row per measured batch (the unit of analysis, n = 30 per cell)

| column | meaning |
|---|---|
| batch_id | `b<block>-<K>-<mode>-<W>`, e.g. `b07-K2-provisioned-W4` |
| block, pos, replicate | block number (= replicate), position inside the randomised block |
| key_design, capacity_mode, configuration, workload, table | the cell |
| seed | decides keys, read/write mix and K3 shards (batches are reproducible) |
| attempted, succeeded, throttled, errors | operation counts over all Lambdas of the batch |
| throttle_rate | throttled / attempted (throttles are never retried or dropped) |
| reads, writes | operation mix actually issued |
| rcu, wcu | capacity units consumed, summed from the API `ConsumedCapacity` of every call |
| latency_mean_ms, latency_p50_ms, latency_p95_ms, latency_p99_ms | service time of successful calls (merged raw records) |
| response_p99_ms | from the planned send time - includes generator backlog |
| wall_s, throughput_ops_s | batch length and successful operations per second |
| hot_rank_share | share of operations on the hottest 10% of keys (should be about 0.90) |
| t_start_epoch, t_end_epoch | batch window (used for CloudWatch) |
| cold_contaminated | a measured invocation ran in a cold Lambda environment (excluded from primary tables) |
| lambdas, rate_scale, time_scale | driver set-up (1.0 / 1.0 in the main campaign) |
| data_source | `live` (Lambda backend) - `moto-smoke` / `local` rows are never results |
| prov_rcu_avg, prov_wcu_avg, prov_source | provisioned capacity during the batch (`cloudwatch` after collect_metrics.py, `config` before) |
| cost_usd, cost_per_10k, cost_consumed_eq_usd, cost_per_10k_consumed_eq | added by the analysis from `config/prices.yaml` |

## `cloudwatch.csv` - one row per batch

`cw_ConsumedReadCapacityUnits`, `cw_ConsumedWriteCapacityUnits`, `cw_ReadThrottleEvents`,
`cw_WriteThrottleEvents` (sums over the batch's whole minutes) and
`cw_ProvisionedReadCapacityUnits`, `cw_ProvisionedWriteCapacityUnits` (averages).

## `raw/<batch_id>.csv.gz` - one row per operation

`seq, t_planned_s, t_start_s, latency_ms, response_ms, op (R/W), order, rank, ok, throttled, code, units`

## Recomputing a cost figure by hand

    on-demand:   cost = rcu * 0.0000001415 + wcu * 0.000000705
    provisioned: cost = (prov_rcu_avg * 0.000147 + prov_wcu_avg * 0.000735) * wall_s / 3600
    cost_per_10k = cost / succeeded * 10000

(eu-west-1 prices from `config/prices.yaml`, publication date 2026-09-11.)
