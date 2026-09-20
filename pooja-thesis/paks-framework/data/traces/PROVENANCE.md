# Dataset provenance — Pooja PAKS (formal CA2)

**Binding:** Google Cluster Trace / Alibaba Cluster Trace for LSTM workload
prediction. See `../../../DATA_GAPS.md`.

## Present: Google Cluster Data version 1 (2010, 7-hour Borg cell)

| Field | Value |
|-------|--------|
| Name | Google Cluster Data (version 1 / “TraceVersion1”) |
| Announced | January 2010 (Google research blog: “Google cluster data”) |
| Canonical docs | https://github.com/google/cluster-data/blob/master/TraceVersion1.md |
| Download URL | http://commondatastorage.googleapis.com/clusterdata-misc/google-cluster-data-1.csv.gz |
| License | [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| SHA1 (gzip) | `98c87f059aa1cc37f1e9523ac691ee0fd5629188` (verified 2026-09-20) |
| Size (gzip) | 31 245 901 bytes |
| Schema | space-separated: `Time ParentID TaskID JobType NrmlTaskCores NrmlTaskMem` |
| Granularity | 5-minute task reports; `Time` is seconds from start of collection |
| Rows parsed | 3 535 029 data rows; 76 distinct `Time` values (90 000 … 112 500, step 300 s) |
| What this is | A **public Google cluster-trace** sample (one cell, ~7 hours). |
| What this is not | GCT 2011 (29-day) or Borg 2019 (eight cells); **not Alibaba**. |

### Aggregation (deterministic; no invented values)

From the SHA1-verified gzip:

1. **Cluster series** (`gct2010_cluster_cpu.csv`): for each `Time`,
   `cpu_cores_sum = Σ NrmlTaskCores`, `mem_sum = Σ NrmlTaskMem`,
   `n_tasks = count(rows)`. Used as the 1-D cluster workload for the
   HPA vs PAKS scaling loop.
2. **Job series** (`gct2010_job_cpu_series.csv.gz`): for each `ParentID` (job)
   with **≥ 12** distinct times, `cpu_cores_sum` per time. Used as LSTM
   windows. Jobs with fewer than 12 bins are dropped (not imputed).

Re-create from raw (after `python scripts/fetch_public_trace_slice.py`):

```bash
python scripts/fetch_public_trace_slice.py --aggregate-only
```

Raw gzip is gitignored (`data/raw/`). Derived series are committed so LSTM
training does not require a 30 MiB refetch.

### Citation

Wilkes, J. / Google. *Google cluster data* (2010 trace). CC-BY.
Documentation: https://github.com/google/cluster-data/blob/master/TraceVersion1.md

## Absent (fail-closed)

- GCT 2011 `task_usage` / `task_events` parts
- Borg 2019 `instance_usage` / `instance_events`
- Any Alibaba `machine_usage` / `batch_task` dump
