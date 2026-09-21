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
| What this is not | Full GCT 2011 (29-day) or Borg 2019 (eight cells). |

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

## Present: GCT 2011 single public shard (sample — not full cell)

| Field | Value |
|-------|--------|
| Name | Google Cluster Data 2011 (`clusterdata-2011-2`) |
| Canonical docs | https://github.com/google/cluster-data/blob/master/ClusterData2011_2.md |
| Object | `task_usage/part-00000-of-00500.csv.gz` |
| URL | https://storage.googleapis.com/clusterdata-2011-2/task_usage/part-00000-of-00500.csv.gz |
| SHA256 | `841254d3bc4199c26c82890dcd6bc87fcfb1ff23d75be8e39f0337f0ed1c6e28` |
| Size | 91 723 415 bytes |
| Derived | `gct2011_part00000_cluster_cpu.csv` (17 × 300 s bins); `gct2011_part00000_job_cpu_series.csv.gz` |
| What this is | One public GCS shard of the 2011 `task_usage` dump. |
| What this is not | The full 500-part / ~29-day cell. |

Fetch + aggregate: `python scripts/fetch_extended_trace_samples.py`

## Present: Alibaba cluster-trace-v2018 machine_usage RANGE sample

| Field | Value |
|-------|--------|
| Name | Alibaba Cluster Trace v2018 `machine_usage` |
| Canonical docs | https://github.com/alibaba/clusterdata/blob/master/cluster-trace-v2018/trace_2018.md |
| Full object URL | http://aliopentrace.oss-cn-beijing.aliyuncs.com/v2018Traces/machine_usage.tar.gz |
| Full object size | 1 774 523 160 bytes |
| Local sample | first **64 MiB** via HTTP `Range` (`machine_usage.tar.gz.partial64m`) |
| Sample SHA256 | `49396e44de5d6bdee04b99bfdea19adafaeee891e3c1bd40117e2ece1192f378` |
| Also fetched | `machine_meta.tar.gz` SHA256 `b5b1b786b22cd413a3674b8f2ebfb2f02fac991c95df537f363ef2797c8f6d55` |
| Derived | `alibaba_v2018_machine_usage_sample_cluster_cpu.csv` (300 s mean CPU%) |
| What this is | A verified byte-range sample of the public OSS object. |
| What this is not | The full 1.7 GiB `machine_usage.tar.gz`. |

SHA index: `SAMPLE_SHA256.txt`.

## Absent (fail-closed)

- Remaining GCT 2011 `task_usage` parts (001–499) / full 29-day join
- Borg 2019 `instance_usage` / `instance_events`
- Full Alibaba `machine_usage.tar.gz` (1.7 GiB) and other v2018 tables
