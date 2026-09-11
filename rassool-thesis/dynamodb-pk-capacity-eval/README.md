# dynamodb-pk-capacity-eval

**Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads**

Rasool Basha Durbesula - 24205478 - MSc Cloud Computing, National College of Ireland

Baseline: Pantelić et al. (2026) 'Benchmarking SQL and NoSQL persistence in
microservices under variable workloads', *Future Internet* 18(1), 53,
doi:[10.3390/fi18010053](https://doi.org/10.3390/fi18010053) - its latency and
throughput measures are kept; throttles, consumed RCU/WCU and cost per 10k
operations are added, because a self-hosted node has none of them.

> **Status.** The artefact is built and tested offline. It has **not** been run
> against AWS yet (that needs the student's own account and budget, see
> `RUNBOOK.md`). `results/` holds the schema only and every result table is a
> `[TO BE FILLED FROM EXPERIMENT]` placeholder - no latency, throttle, capacity
> or cost figure has been made up.

## Design (3 x 2 x 4, n = 30)

| Factor | Levels |
|---|---|
| Key design | K1 `orderId` - K2 `customerId` + `orderTs` - K3 `orderId#shard` (N = 10, random shard per write, reads gather all 10) |
| Capacity mode | on-demand - provisioned with target-tracking auto-scaling (bounds sized per key design) |
| Workload (from Lambda) | W1 95/5 read/write, W2 30/70, W3 50/50 at 200 ops/s; W4 50/50, 60 s at 200 ops/s + 30 s at 1,000 ops/s |

1,000,000 synthetic orders over 10,000 customers, Zipf s = 1.070916 (90% of
operations on 10% of keys), 1 KB items. 30 batches per cell in 30 randomised
blocks; 120 s settling and Lambda warm-up before every batch; no SDK retries.
Two-way ANOVA with interaction (or aligned rank transform), Tukey simple
effects, Holm over 12 tests - see `docs/ANALYSIS_PLAN.md`.

## Quick start (no AWS)

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
make test          # unit tests + handler/seed against moto
make tf-check      # terraform fmt + validate
make design        # capacity plan + hot-key predictions
make smoke         # whole pipeline on in-memory DynamoDB (moto), ~2 minutes - NOT DynamoDB data
python scripts/budget_estimate.py   # what the real campaign will cost (~$80 at list prices)
```

The live campaign (seed -> deploy -> warmup -> run-matrix -> collect-metrics ->
analyse -> teardown) is in `RUNBOOK.md`; the full reference is
`configuration_manual/CONFIGURATION_MANUAL.md`.

## Layout

```text
dynamodb-pk-capacity-eval/
├── iac/                   Terraform: tables/ (x6 via for_each), lambda/, iam/, monitoring/
├── workloads/
│   ├── generator/         Zipf sampler, key designs K1-K3, profiles W1-W4
│   ├── lambda_handler/    load generator (open loop, no retries, raw CSV per batch)
│   ├── seed/              1M-item loader (BatchWriteItem x 25)
│   └── matrix.py          randomised blocks, per-Lambda events
├── analysis/              cost_model, stats (ANOVA / ART / Tukey / Holm / joint), analyse, design_checks, pilot_check
├── config/                experiment.yaml (committed factors), prices.yaml (dated), budget_prices.yaml
├── scripts/               run_matrix, collect_metrics, build_lambda, render_tfvars, budget_estimate, check_bib
├── results/SCHEMA.md      schema only - no numbers in the repo
├── report/                section map + generated placeholder tables
├── configuration_manual/  separate from the page limit
├── docs/                  ASSUMPTIONS, ANALYSIS_PLAN, ETHICS
├── bib/references.bib     the 21 papers of the master prompt + 3 AWS docs, all resolved online
└── tests/
```

## What the design checks predict (arithmetic, not results)

`analysis/design_checks/README.md`: the hottest order gets 10.65% of all
operations. With 1 KB items no hot key reaches the documented per-partition
limits (3,000 RCU/s, 1,000 WCU/s) in any main-factorial cell, so throttling
there can only come from table capacity (provisioned tables under the W4 burst).
Only the 32 KB sensitivity run pushes K1/K2's hottest key over the write limit
(~1,704 WCU/s), where K3 spreads it to ~170 per shard key. K3 pays for this on
reads: 10 read units per logical read, so its provisioned read floor is 1,360 RCU
instead of 140.

## Things worth knowing

* `botocore`'s `retries={"max_attempts": 1}` still retries once - the driver uses
  `total_max_attempts: 1`, and a test checks it, so throttles are never hidden.
* Provisioned cost is what the table costs while it serves a batch (capacity x time);
  a consumed-units version is reported next to it as a sensitivity.
* Only `data_source = live` rows are ever analysed as results; the analysis refuses
  to mix sources and stamps anything else "NOT DynamoDB DATA".

## Left for the student

Deploy and run the campaign in their own account, the pilot and any amendment,
the report, the weekly logs and the viva.
