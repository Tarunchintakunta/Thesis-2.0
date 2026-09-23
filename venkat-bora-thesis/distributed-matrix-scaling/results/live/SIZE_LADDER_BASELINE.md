# Venkat CA2 multi-order size ladder (live Free-Tier EC2)

**Date:** 2026-09-22  
**Pack:** `results/live/size_ladder_ladder1/`  
**Topology:** 1× t3.small (scale-up numpy) vs 2× t3.micro (scale-out Dask multi-instance); matched aggregate 2 vCPU; destroy-after.  
**CA2 limb:** growing matrix orders at fixed cores; completion time + peak RSS + avg CPU; timeouts recorded as outcomes.

| n | scale-up elapsed_s | scale-up peak_rss_mb | multi status | multi elapsed_s | multi peak_rss_mb | multi avg_cpu% |
|--:|-------------------:|---------------------:|:------------:|----------------:|------------------:|---------------:|
| 100 | 0.000213 | 35.32 | ok | 0.2442 | 71.79 | 43.8 |
| 250 | 0.002101 | 37.38 | ok | 0.2549 | 72.58 | 42.0 |
| 500 | 0.007588 | 42.40 | ok | 0.2855 | 80.84 | 46.1 |

## Verdict
- **Live size ladder executed** for Free-Tier subset 100 / 250 / 500 (local suite already covers 200–2000).
- **No crossover** in this live range: scale-up remains ≪ multi at every order (**anti-crossover retained** — honest negative for “distribution pays sooner”).
- Multi RSS grows with order (~72 → 81 MB); CPU occupancy ~42–46%.
- No timeouts in this subset (all `ok`); timeout-as-outcome path exercised in harness (`BENCH_TIMEOUT`).
- **Destroy confirmed** 2026-09-22T17:11:41Z; remaining project instances = 0.

## Artefacts
- `campaign_summary.json`
- `n_{100,250,500}/summary.json`
- `scripts/run_ec2_size_ladder.sh`
- `destroy_confirmed.txt`
