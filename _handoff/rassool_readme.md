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
