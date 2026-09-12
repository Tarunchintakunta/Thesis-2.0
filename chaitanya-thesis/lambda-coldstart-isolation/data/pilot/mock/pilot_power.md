# Pilot power check

### Pilot result (mock data, 2026-09-12)

**SYNTHETIC mock pilot - these numbers only test the script. Re-run with the live pilot.**

Sizing: two-sided alpha 0.010 (0.05 / 5), power 0.80, smallest effect 50 ms, pooled SD of the two cells, rank-test ARE 0.864, never below 30.

| cell | intended cold | really cold | median Init (ms) | SD (ms) |
|---|---|---|---|---|
| java-default | 12 | 12 | 769 | 126.7 |
| java-optimised | 12 | 12 | 507 | 77.8 |
| nodejs-default | 12 | 12 | 576 | 131.0 |
| nodejs-optimised | 12 | 12 | 190 | 24.5 |
| python-bytecode | 12 | 12 | 243 | 49.2 |
| python-default | 12 | 12 | 661 | 136.6 |
| python-optimised | 12 | 12 | 165 | 26.4 |

| comparison | n needed per cell |
|---|---|
| H1: python-optimised vs nodejs-optimised | 8 |
| H1: python-optimised vs java-optimised | 37 |
| H1: nodejs-optimised vs java-optimised | 37 |
| H2_python: python-default vs python-optimised | 105 |
| H2_nodejs: nodejs-default vs nodejs-optimised | 97 |
| H2_java: java-default vs java-optimised | 120 |

| phase | planned | recommended | |
|---|---|---|---|
| runtime_compare | 50 | 37 | ok |
| package_size | 50 | 120 | raise |
| memory | 40 | 40 | ok |
| combined | 40 | 40 | ok |

Forced cold by configuration update: 84 of 84 intended-cold calls were really cold.

| idle gap (min) | n | cold | cold fraction | Wilson 95% CI |
|---|---|---|---|---|
| 5 | 8 | 1 | 0.12 | 0.02-0.47 |
| 10 | 8 | 5 | 0.62 | 0.31-0.86 |
| 20 | 8 | 8 | 1.00 | 0.68-1.00 |
| 30 | 8 | 8 | 1.00 | 0.68-1.00 |
| 45 | 8 | 8 | 1.00 | 0.68-1.00 |

Shortest idle gap where at least 95% of the probes were cold: **20 minutes** (small n - check the interval).
