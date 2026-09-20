# Cell summary

**Data: measured on Amazon DynamoDB (eu-west-1).** Live key-cell round: $n{=}1$ block, 100k seeded orders, workloads **W3/W4 only** (W1/W2 still empty). 0 cold-contaminated batches excluded.

| workload | configuration | latency_mean_ms | latency_p95_ms | latency_p99_ms | throughput_ops_s | throttle_rate | cost_per_10k | n | rcu_per_10k | wcu_per_10k |
|---|---|---|---|---|---|---|---|---|---|---|
| W3 | K1-on_demand | 4.344 | 5.838 | 7.047 | 199.9 | 0 | 0.003901 | 1 | 2483 | 5034 |
| W3 | K1-provisioned | 4.364 | 5.796 | 7.339 | 199.9 | 0 | 0.002328 | 1 | 2507 | 4986 |
| W3 | K2-on_demand | 4.482 | 5.883 | 6.948 | 199.9 | 0 | 0.003874 | 1 | 2504 | 4993 |
| W3 | K2-provisioned | 4.354 | 5.765 | 7.499 | 199.9 | 0 | 0.0105 | 1 | 2522 | 4955 |
| W3 | K3-on_demand | 5.01 | 6.116 | 10.32 | 199.9 | 0 | 0.007062 | 1 | 2.498e+04 | 5003 |
| W3 | K3-provisioned | 4.895 | 5.787 | 8.333 | 199.9 | 0 | 0.007128 | 1 | 2.479e+04 | 5042 |
| W4 | K1-on_demand | 4.553 | 5.848 | 7.64 | 466.5 | 0 | 0.003886 | 1 | 2494 | 5011 |
| W4 | K1-provisioned | 4.89 | 6.035 | 10.23 | 466.5 | 0 | 0.000998 | 1 | 2490 | 5019 |
| W4 | K2-on_demand | 4.803 | 5.876 | 9.631 | 466.5 | 0 | 0.003899 | 1 | 2484 | 5032 |
| W4 | K2-provisioned | 4.597 | 5.848 | 7.667 | 466.5 | 0 | 0.000998 | 1 | 2497 | 5006 |
| W4 | K3-on_demand | 5.246 | 6.265 | 10.62 | 466.5 | 0 | 0.007063 | 1 | 2.503e+04 | 4993 |
| W4 | K3-provisioned | 5.356 | 6.223 | 11.49 | 466.5 | 0 | 0.005567 | 1 | 2.506e+04 | 4989 |
