# Pilot power check

### Pilot result (mock data, 2026-09-11)

**SYNTHETIC mock pilot - these numbers only test the script. Re-run with the live pilot.**

Sizing: two-sided alpha 0.010 (0.05 / 5), power 0.80, smallest effect 50 ms, pooled SD of the two cells, rank-test ARE 0.864, never below 30.

| cell | intended cold | really cold | median Init (ms) | SD (ms) |
|---|---|---|---|---|
| java-default | 12 | 12 | 836 | 163.6 |
| java-optimised | 12 | 12 | 544 | 83.2 |
| nodejs-default | 12 | 12 | 535 | 110.3 |
| nodejs-optimised | 12 | 12 | 189 | 41.4 |
| python-default | 12 | 12 | 648 | 87.4 |
| python-optimised | 12 | 12 | 158 | 36.5 |

| comparison | n needed per cell |
|---|---|
| H1: python-optimised vs nodejs-optimised | 17 |
| H1: python-optimised vs java-optimised | 45 |
| H1: nodejs-optimised vs java-optimised | 47 |
| H2_python: python-default vs python-optimised | 49 |
| H2_nodejs: nodejs-default vs nodejs-optimised | 76 |
| H2_java: java-default vs java-optimised | 183 |

| phase | planned | recommended | |
|---|---|---|---|
| runtime_compare | 50 | 47 | ok |
| package_size | 50 | 183 | raise |
| memory | 40 | 40 | ok |
| combined | 40 | 40 | ok |

Forced cold by configuration update: 72 of 72 intended-cold calls were really cold.

| idle gap (min) | n | cold | cold fraction | Wilson 95% CI |
|---|---|---|---|---|
| 5 | 8 | 1 | 0.12 | 0.02-0.47 |
| 10 | 8 | 4 | 0.50 | 0.22-0.78 |
| 20 | 8 | 7 | 0.88 | 0.53-0.98 |
| 30 | 8 | 8 | 1.00 | 0.68-1.00 |
| 45 | 8 | 8 | 1.00 | 0.68-1.00 |

Shortest idle gap where at least 95% of the probes were cold: **30 minutes** (small n - check the interval).
