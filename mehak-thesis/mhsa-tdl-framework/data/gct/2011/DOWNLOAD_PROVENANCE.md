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

Parent/sibling `gsutil -m cp gs://clusterdata-2011-2/...` was observed stuck at a
0-byte `*.csv.gz_.gstmp` for `machine_events`. This pass reused the **same
official bucket objects** over public HTTPS instead of starting a second
multi-GB gsutil mirror.

## Minimum-viable subset landed

| Object | Bytes | SHA-256 |
|--------|------:|---------|
| `machine_events/part-00000-of-00001.csv.gz` | 347211 | `fc44b8d2b33a96a261382488789855be7a0ce338888c99930ff45cb592249664` |
| `task_events/part-00000-of-00500.csv.gz` | 4139742 | `eae977d521bc6ed5d8deef56f1e06009d41844d4eb9a7e308e610d68e1b10f18` |
| `task_events/part-00001-of-00500.csv.gz` | 924634 | `c122f250cf1f9817dc722a5b7457eb5caf122619accfada078de66d40f311501` |
| `task_usage/part-00000-of-00500.csv.gz` | 91723415 | `841254d3bc4199c26c82890dcd6bc87fcfb1ff23d75be8e39f0337f0ed1c6e28` |

Machine-readable copy: `DOWNLOAD_PROVENANCE.json` (written by the fetcher).

## Still missing vs full 2011 dump (~41 GB compressed)

- Remaining `task_events` parts `00002`–`00499`
- Remaining `task_usage` parts `00001`–`00499`
- `job_events/*`, `machine_attributes/*`
- Entire 2019 Borg eight-cell family

Join evidence on this subset (measured 2026-09-20): usage keys are a subset of
event keys (179427/179427 overlap); FAIL tasks in usage = 479; EVICT in usage =
5787. Loader prefers FAIL-family series so event-forced windows are not dropped
by the first-N cap (`fail_forced_windows=489` on N=12000 in `results/gct/`).
That is enough for a first formal run; it is **not** the full 29-day cell.
