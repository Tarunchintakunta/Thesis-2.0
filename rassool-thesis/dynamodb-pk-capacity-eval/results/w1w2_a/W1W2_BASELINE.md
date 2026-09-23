# Rasool W1/W2 key-cell pack (closes dated W1/W2 deferral)

**Date:** 2026-09-22/23  
**Pack:** `results/w1w2_a/`  
**Region:** eu-west-2 · prefix `ddbpkw12a` · **destroy_confirmed=yes**  
**Protocol:** W1+W2 × K1/K2/K3 × on_demand/provisioned · n=1 key-cell · 18k ops/cell · destroy-after

## Coverage

12/12 cells on disk (`batches.csv`). Workloads present: **W1, W2**. (W3/W4 remain in `final_{1,2,3}/`.)

## Exploratory request-level KW (pseudo-replication; not confirmatory ANOVA)

| Stratum | Kruskal H | p | median latency ms (K1/K2/K3) |
|---------|----------:|--:|------------------------------|
| W1-on_demand | 2.8e4 | ≈0 | 3.813 / 3.860 / 5.077 |
| W1-provisioned | 1.48e4 | ≈0 | 3.929 / 3.931 / 4.8165 |
| W2-on_demand | 427 | 1.68e-93 | 5.709 / 5.487 / 5.323 |
| W2-provisioned | 1.55e3 | ≈0 | 5.341 / 5.466 / 5.473 |

Throttle rate = 0 across cells. Throughput ≈ 200 ops/s.

## Honesty

- Batch two-way ANOVA **not identified** at n=1 (same as W3/W4 key-cell packs).
- Request-level KW is exploratory (pseudo-replication).
- Confirmatory authority for factor effects remains **pooled final-3 ANOVA on W3/W4**.
- Do **not** market “full W1–W4 confirmatory ANOVA 100%.”

## Artefacts

`batches.csv`, `cloudwatch.csv`, `raw/*.csv.gz`, `hypotheses_keycell_n1.{json,md}`, `PROVENANCE.txt`, `destroy_confirmed.txt`
