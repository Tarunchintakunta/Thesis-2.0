# Assumptions and design decisions

Rasool Basha Durbesula - 24205478

What the master prompt left open, what was picked, and why. Later changes go
underneath with a date and a reason (they are also amendments in ANALYSIS_PLAN.md).

## Infrastructure

| # | Decision | Why |
|---|---|---|
| I1 | **Terraform** (not CDK). One `tables` module, called with `for_each` over the six key-design x capacity-mode pairs. | Declarative, the six tables come from the same code with only two parameters changing, `terraform validate` runs in CI without an AWS account, provider versions are pinned in `.terraform.lock.hcl`, and `terraform destroy` is the teardown. CDK would add a Node/jsii toolchain for no gain here. |
| I2 | Region `eu-west-1`, table class STANDARD, point-in-time recovery off, no GSIs, no streams. | Controls; GSIs / DAX / multi-region are future work (master prompt 8). |
| I3 | Every resource is tagged `project=dynamodb-pk-capacity`, `student=24205478` through the provider's `default_tags`. | Master prompt 3.2. |
| I4 | Provisioned (C2) tables are sized **per key design**: the minimum covers the base rate (200 ops/s) of the heaviest of W1-W3 at the 70% auto-scaling target; the maximum is 5x the minimum. Result: K1/K2 140-700 RCU, 200-1000 WCU; K3 1360-6800 RCU, 200-1000 WCU (`analysis/design_checks/capacity_plan.csv`). | "Equivalent load" means the same offered operations. A provisioned table sized the way a careful engineer would size it for that design is the fair comparison; one fixed size for all designs would make K3 throttle only because of its own read amplification. The W4 burst (5x) is left to auto-scaling and burst capacity, which is exactly what the capacity-mode question is about. |
| I5 | `seed_mode=true` raises the write floor of the provisioned tables to 2,000 WCU while the 1M items are loaded, then it is switched back. | Loading 1M items at 200 WCU would take ~1.4 h per table. |

## Data and keys

| # | Decision | Why |
|---|---|---|
| D1 | 1,000,000 orders `o0000000..o0999999`, 10,000 customers; order i belongs to customer `(i x 7919 + 13) mod 10000`, so every customer has exactly 100 orders. | Master prompt 2.2; synthetic, no personal data. 7919 is prime and coprime with 10,000. |
| D2 | Items are padded to just under 1 KB including attribute names (`workloads/generator/keys.py`), so a write costs exactly 1 WCU. | Otherwise attribute-name bytes would push items over 1 KB and double the write cost. |
| D3 | **K3 shard rule**: N = 10; every PutItem picks a shard uniformly at random (`orderId#0..9`); a read is a BatchGetItem of all 10 shard keys and the newest `version` wins; seeding puts each order at shard `index mod 10`. | Random suffixes are the AWS-documented way to spread hot *writes*. The price is paid on reads (10 keys per read, and a key that does not exist still costs the minimum read unit), which is part of what the study measures. |
| D4 | Reads are eventually consistent (GetItem default): 0.5 RCU per 4 KB. | Default behaviour; strongly consistent reads would double read cost and are not a factor here. |
| D5 | Zipf exponent **s = 1.070916**, calibrated so the hottest 10% of the 1M keys get 90.0% of operations (top 1%: 78%; the single hottest order: 10.65%). Ranks are mapped to orders through a fixed random permutation (seed 24205478). | Master prompt 2.2 asks for ~90/10 and forbids uniform access. |

## Driver and measurement

| # | Decision | Why |
|---|---|---|
| M1 | Load comes from 4 concurrent Lambda invocations (arm64, 1,769 MB = 1 vCPU, 32 threads each), each taking a quarter of the rate. | One Python process cannot issue 1,000 boto3 calls/s reliably (GIL); 4 processes keep the generator from being the bottleneck. Generator lag is recorded (`response_p99_ms`, `lag_ms_p99`). |
| M2 | **No SDK retries**: `retries={"total_max_attempts": 1}`. | Throttles must reach the record. Note that botocore's `"max_attempts": 1` still allows one retry (it counts retries, not attempts) - a test checks the real setting. |
| M3 | Open-loop arrivals at fixed spacing (1/rate). `latency_ms` = service time of the call (the Pantelic-style latency); `response_ms` = from the planned send time, so it includes any backlog. | Closed-loop generators hide slowdowns (coordinated omission). |
| M4 | Batch length: 90 s for W1-W3, two burst cycles (180 s) for W4. Settling: 120 s at the profile's base rate before every measured batch; 2 warm-up invocations before that. | Master prompt 2.4: warm Lambdas, fixed settling interval, reported. The pilot checks whether 120 s is enough (drift in the first vs last third of each batch). |
| M5 | A batch whose measured invocation started in a cold Lambda environment is kept but flagged `cold_contaminated` and left out of the primary tables. | Master prompt 2.4: cold-start tails are excluded from primary latency tables. |
| M6 | Throttle = `ProvisionedThroughputExceededException`, `ThrottlingException`, `RequestLimitExceeded`, or unprocessed keys in a K3 BatchGetItem. | Batch calls report throttling as unprocessed keys, not as an exception. |
| M7 | Consumed RCU/WCU come from `ReturnConsumedCapacity=TOTAL` on every call (exact per operation); CloudWatch `Consumed*CapacityUnits` is the cross-check. | Master prompt 2.3. |

## Cost

| # | Decision | Why |
|---|---|---|
| C1 | On-demand cost = consumed RRU/WRU x unit price. Provisioned cost = mean provisioned RCU/WCU during the batch x hours x capacity-hour price (what the table costs while it serves the batch, used or not). A "consumed-equivalent" provisioned cost is reported as a sensitivity. | The master prompt asks for published prices x consumed units; for provisioned tables that alone would ignore the idle headroom you pay for, so both are shown and the primary one is stated here, before data. |
| C2 | Prices: eu-west-1 list prices from the AWS Price List API, publication date 2026-09-11 (`config/prices.yaml`, refresh with `analysis/fetch_prices.py`). Free tier ignored. Storage, backups, data transfer and the driver Lambda are excluded from cost per 10k ops. | Recomputable figures (master prompt 2.4). |
| C3 | The campaign is **not free-tier-safe** despite the proposal's wording: 720 batches, ~46.5 h of load, request path ~$15 at list prices, plus the provisioned tables' hourly charge for as long as they exist, seeding and the driver Lambda (see RUNBOOK budget table). | Honest budget; the student should confirm it with the supervisor and destroy the stack straight after the campaign. |

## What the design checks predict (arithmetic, not results)

With 1 KB items the hottest partition-key value stays below the documented
per-partition limits in every main-factorial cell, so throttling in the main
campaign can only come from table-level capacity (C2 under the W4 burst, if
burst capacity runs out). Only the 32 KB sensitivity runs push K1/K2's hottest
key past 1,000 WCU/s under W4 (~1,704 WCU/s), where K3 spreads it to ~170 per
shard key. A main campaign with very few throttles would therefore be a real
result, not a failed experiment.
