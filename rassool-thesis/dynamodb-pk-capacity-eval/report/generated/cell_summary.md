# Cell summary (6 configurations x 4 workloads)

**Live key-cell round (2026-09-20):** W3/W4 × K1–K3 × on_demand/provisioned = **12/12 measured** from `results/batches.csv` (`data_source=live`, `blocks=1`, `orders=100000`, eu-west-1).  
**Missing:** all W1 and W2 cells — still `[MISSING — not in key-cell round]`.  
**Not computed:** live ANOVA / KS — do not invent. Cost = list-price proxy via `analysis/cost_model.py` + `config/prices.yaml` (not Cost Explorer).

| workload | configuration | latency_mean_ms | latency_p95_ms | latency_p99_ms | throughput_ops_s | throttle_rate | cost_per_10k |
|---|---|---|---|---|---|---|---|
| W1 | K1-on_demand | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W1 | K1-provisioned | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W1 | K2-on_demand | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W1 | K2-provisioned | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W1 | K3-on_demand | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W1 | K3-provisioned | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W2 | K1-on_demand | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W2 | K1-provisioned | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W2 | K2-on_demand | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W2 | K2-provisioned | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W2 | K3-on_demand | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W2 | K3-provisioned | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] | [MISSING — not in key-cell round] |
| W3 | K1-on_demand | 4.344 | 5.838 | 7.047 | 199.922 | 0.0 | 0.003901 |
| W3 | K1-provisioned | 4.364 | 5.796 | 7.339 | 199.925 | 0.0 | 0.002328 |
| W3 | K2-on_demand | 4.482 | 5.883 | 6.948 | 199.918 | 0.0 | 0.003874 |
| W3 | K2-provisioned | 4.354 | 5.765 | 7.499 | 199.919 | 0.0 | 0.010498 |
| W3 | K3-on_demand | 5.010 | 6.116 | 10.320 | 199.919 | 0.0 | 0.007062 |
| W3 | K3-provisioned | 4.895 | 5.787 | 8.333 | 199.920 | 0.0 | 0.007128 |
| W4 | K1-on_demand | 4.553 | 5.848 | 7.640 | 466.531 | 0.0 | 0.003886 |
| W4 | K1-provisioned | 4.890 | 6.035 | 10.232 | 466.532 | 0.0 | 0.000998 |
| W4 | K2-on_demand | 4.803 | 5.876 | 9.631 | 466.530 | 0.0 | 0.003899 |
| W4 | K2-provisioned | 4.597 | 5.848 | 7.667 | 466.533 | 0.0 | 0.000998 |
| W4 | K3-on_demand | 5.246 | 6.265 | 10.623 | 466.483 | 0.0 | 0.007063 |
| W4 | K3-provisioned | 5.356 | 6.223 | 11.490 | 466.531 | 0.0 | 0.005567 |

Source: `results/keycell_summary.csv` (derived from `results/batches.csv` with `add_costs`).
