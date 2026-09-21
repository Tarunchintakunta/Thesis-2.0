# GCT 2011 download provenance (formal CA2)

**Not synthetic.** Files below are the official Google Cluster Data 2011
(`clusterdata-2011-2`, trace v2.1) objects.

| Field | Value |
|-------|--------|
| Canonical repo | https://github.com/google/cluster-data |
| Schema | https://github.com/google/cluster-data/blob/master/ClusterData2011_2.md |
| Bucket (gs) | `gs://clusterdata-2011-2` |
| Bucket (HTTPS, same objects) | https://storage.googleapis.com/clusterdata-2011-2 |
| License | CC-BY 4.0 |
| Trace | Borg cell, ~29 days starting 2011-05-01 19:00 EDT |
| Local root | `mhsa-tdl-framework/data/gct/2011/` |
| Fetcher | `scripts/download_gct_2011.py` (idempotent; skips complete files) |

## Expanded subset landed (SHA-256 in `DOWNLOAD_PROVENANCE.json`)

| Object | Bytes | SHA-256 (prefix) |
|--------|------:|------------------|
| `machine_events/part-00000-of-00001.csv.gz` | 347211 | `fc44b8d2…` |
| `task_events/part-00000-of-00500.csv.gz` | 4139742 | `eae977d5…` |
| `task_events/part-00001-of-00500.csv.gz` | 924634 | `c122f250…` |
| `task_events/part-00002-of-00500.csv.gz` | 1821031 | `3534b71a…` |
| `task_events/part-00003-of-00500.csv.gz` | 1335641 | `23b3df1b…` |
| `task_usage/part-00000-of-00500.csv.gz` | 91723415 | `841254d3…` |
| `task_usage/part-00001-of-00500.csv.gz` | 87188987 | `1fa83e39…` |

Join evidence on this subset: fail-series-first → `fail_forced_windows=981` on N=12000 (`results/gct/`). Enough for the formal metric suite; **not** the full 29-day cell.

## Optional remainder (beyond CA2 floor)

- Remaining `task_events` / `task_usage` parts (~41 GB compressed full dump)
- `job_events/*`, `machine_attributes/*`
- Entire 2019 Borg eight-cell family

Scoped out with rationale in `mehak-thesis/DESIGN_RATIONALE_BEYOND_CA2.md` — not open floor blockers.
