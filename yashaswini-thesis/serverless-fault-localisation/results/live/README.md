# Live Leg 3 — lite overhead (measured)

**Date:** 2026-09-20  
**Config:** `configs/experiment_lite_overhead.yaml` (5 min × 3 conditions @ 1 rps)  
**Stack:** Terraform `faultlab` in `eu-west-1` — **destroyed after**  
**Authoritative summary:** `overhead.json` (from `scripts/collect_overhead.py --summarise`)  
**Raw run:** `data/runs/live_lite_overhead/`

## Conditions (measured)

| Condition | Requests | bytes / 1000 req | traces | median latency ms | error share |
|-----------|--------:|-----------------:|-------:|------------------:|------------:|
| full | 300 | 19 000 061 | 511 | 916.24 | 0.00 |
| policy | 300 | 3 739 927 | 51 | 875.63 | 0.01 |
| off | 300 | 1 251 573 | 0 | 917.98 | 0.00 |

- **Reduction policy vs full:** 0.803 (80.3%) — meets ≥50% volume bar on this lite cell  
- **Cost / 1M req (list-price):** full ≈ \$10.93; policy ≈ \$2.25  
- Learned lower bound: median $4.23\times10^{5}$ bytes/1000 ($n{=}8$ RE2-OB checkoutservice parquet; compressed lower bound)  

Lite is directional measured evidence, not confirmatory 30-minute cells (`configs/experiment.yaml`).
