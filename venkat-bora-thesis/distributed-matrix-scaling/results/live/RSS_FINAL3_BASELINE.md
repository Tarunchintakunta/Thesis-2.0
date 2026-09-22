# Venkat RSS/CPU final-3 baseline (instrumented live EC2)

**Date:** 2026-09-22
**Topology:** 1× t3.small (scale-up) vs 2× t3.micro (scale-out multi-instance); n=250; destroy-after.
**Artefact:** scripts/quick_bench.py + dist_bench.py (peak_rss_mb, avg_cpu_percent).

| Round | scale-up elapsed_s | scale-up peak_rss_mb | multi elapsed_s | multi peak_rss_mb | multi avg_cpu% | status |
|------:|-------------------:|---------------------:|----------------:|------------------:|---------------:|:------:|
| 1 | 0.002467 | 37.43359375 | 0.2532 | 72.48828125 | 44.44 | ok |
| 2 | 0.001914 | 0.0 | 0.2736 | 72.46875 | 46.1 | ok |
| 3 | 0.002016 | 37.3359375 | 0.2661 | 72.84375 | 38.61666666666667 | ok |

## Verdict
- **Positive:** Peak RSS + CPU instrumented on live EC2; multi-instance RSS ~72–74 MB consistent across 3 rounds; destroy-after each.
- **Note:** Scale-up numpy matmul is sub-ms; peak_rss sampler can read ~0 on ultra-short runs — treat multi-instance RSS/CPU as primary RQ limb evidence.
- **Residual:** Size ladder (100/250/500 with timeouts-as-outcomes) still soft if RQ requires multi-order sizes.

