# Exact missing datasets — Pooja formal CA2 (PAKS)

**Binding CA2:** `Pooja_25120921_CA2.docx` (formal PAKS)  
**Required datasets:** Google Cluster Trace **and/or** Alibaba Cluster Trace, used to train a workload **LSTM** (TensorFlow named in the CA2 resources table).  
**AWS / K8s:** Formal method is a Kubernetes cluster on **AWS EC2 + S3 + CloudWatch**. **Not deployed this pass.**

## What is present (minimal public GCT slice)

| Artefact | Path | Role |
|----------|------|------|
| Google Cluster Data **v1** (2010, ~7 h Borg cell, CC-BY) | download: `paks-framework/data/raw/google-cluster-data-1.csv.gz` (gitignored, 30 MiB) | Canonical public GCT family member; SHA1 `98c87f059aa1cc37f1e9523ac691ee0fd5629188` |
| Derived cluster CPU series (76 × 5 min bins) | `paks-framework/data/traces/gct2010_cluster_cpu.csv` | Scaling-loop workload (trace-derived) |
| Derived per-job CPU series (jobs with ≥12 bins) | `paks-framework/data/traces/gct2010_job_cpu_series.csv.gz` | LSTM train/test windows (trace-derived) |
| Provenance | `paks-framework/data/traces/PROVENANCE.md` | License, URL, aggregation rules |

This **is** Google cluster-trace data. It is **not** the 2011 29-day cell or the 2019 eight-cell Borg traces named in many PAKS-style papers, and it is **not** Alibaba.

## Still missing (fail-closed if requested)

### Google Cluster Data 2011 (Borg, ~29 days)

Canonical: https://github.com/google/cluster-data (`ClusterData2011_2.md`)  
Bucket: `gs://clusterdata-2011-2` / `https://storage.googleapis.com/clusterdata-2011-2/`

| Expected local path | Role |
|---------------------|------|
| `paks-framework/data/gct/2011/task_usage/part-*-of-*.csv.gz` | CPU/memory usage (workload features) |
| `paks-framework/data/gct/2011/task_events/part-*-of-*.csv.gz` | Optional lifecycle context |

Loader: `--dataset gct2011` → `FileNotFoundError` until at least one `task_usage` part exists.

### Google Borg traces 2019

Canonical: https://github.com/google/cluster-data (`ClusterData2019.md`)

| Expected local path | Role |
|---------------------|------|
| `paks-framework/data/gct/2019/<cell>/instance_usage/*` | Usage time series |
| `paks-framework/data/gct/2019/<cell>/instance_events/*` | Optional events |

`--dataset gct2019` fail-closed.

### Alibaba Cluster Trace

Canonical: https://github.com/alibaba/clusterdata  
Common public families: cluster-trace-v2018 (`machine_usage` / `batch_task`) and later releases.

| Expected local path | Role |
|---------------------|------|
| `paks-framework/data/alibaba/**/machine_usage*.csv*` | Machine CPU/memory time series |
| `paks-framework/data/alibaba/**/batch_task*.csv*` | Optional batch arrivals |

`--dataset alibaba` fail-closed. **No Alibaba files are in this repo.**

## TensorFlow runtime

Formal CA2 resources name **TensorFlow** for the LSTM. This evaluation host runs **CPython 3.14**, which has no supported TensorFlow wheel at time of writing. The artefact trains a **vanilla LSTM (NumPy, BPTT)**. `--backend tensorflow` raises `ImportError` (fail-closed) rather than silently substituting MLP.

MLP `MLPRegressor` remains only on the **proxy** path (`src/proxy/`).

## Synthetic / NimbusGuard simulator

`src/data/workload_simulator.py` is **PROXY**. It must not be used as a silent fallback when `--dataset gct*`, `--dataset alibaba`, or `--dataset gct` is requested.

## Loader contract

`paks-framework/src/data/trace_loader.py`:

- `--dataset gct2010` / default formal slice: load committed derived series (or re-aggregate from SHA1-verified raw gzip).
- `--dataset gct`: use 2011 if present, else 2019, else 2010 sample **with provenance stating the residual**.
- `--dataset gct2011` / `gct2019` / `alibaba`: **raise** with this checklist.
- `--dataset synthetic`: explicit proxy only; `meta["proxy"]=True`.

## Not a substitute for live K8s-on-AWS

Dry-run `apps/v1` Scale patches and simulated util/latency/cost **do not** close the formal AWS EC2+S3+CloudWatch Kubernetes experiment.
